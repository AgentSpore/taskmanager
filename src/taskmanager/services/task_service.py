"""
Task service for TaskManager.

Business logic for task management, AI-powered features, and analytics.
"""

import time
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from loguru import logger
from aiosqlite import Connection

from ..core.database import get_db
from ..schemas.task import (
    TaskCreate,
    TaskRead,
    TaskUpdate,
    TaskListResponse,
    TaskAnalyticsResponse,
    TaskAnalytics,
    Priority,
    Status,
    TaskSuggestion,
)
from ..schemas.category import CategoryRead


class TaskService:
    """
    Service for task management operations.
    """
    
    def __init__(self, db: Connection):
        self.db = db
    
    async def create_task(self, task: TaskCreate) -> TaskRead:
        """
        Create a new task with AI-powered suggestions.
        """
        try:
            # Extract tags and dependencies for separate tables
            tags = task.tags
            depends_on = task.depends_on
            
            # Create main task
            cursor = await self.db.execute("""
                INSERT INTO tasks (
                    title, description, priority, status, category_id, 
                    due_date, estimated_hours, actual_hours, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.title,
                task.description,
                task.priority.value,
                task.status.value,
                task.category_id,
                task.due_date,
                task.estimated_hours,
                task.actual_hours,
                1  # TODO: Get from authentication context
            ))
            
            task_id = cursor.lastrowid
            
            # Add task tags
            if tags:
                await self.db.executemany(
                    "INSERT INTO task_tags (task_id, tag) VALUES (?, ?)",
                    [(task_id, tag) for tag in tags]
                )
            
            # Add task dependencies
            if depends_on:
                await self.db.executemany(
                    "INSERT INTO task_dependencies (task_id, depends_on_id) VALUES (?, ?)",
                    [(task_id, dep_id) for dep_id in depends_on]
                )
            
            # Get the created task
            created_task = await self.get_task(task_id)
            
            # AI-powered suggestions if enabled
            if task.description and len(task.description) > 50:
                await self._suggest_priority_improvements(created_task)
            
            logger.info(f"Task created successfully: {task_id}")
            return created_task
            
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise
    
    async def get_task(self, task_id: int) -> Optional[TaskRead]:
        """
        Get a specific task by ID.
        """
        try:
            cursor = await self.db.execute("""
                SELECT t.*, c.name as category_name
                FROM tasks t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.id = ?
            """, (task_id,))
            
            row = await cursor.fetchone()
            
            if not row:
                return None
            
            return self._row_to_task_read(row)
            
        except Exception as e:
            logger.error(f"Failed to get task: {e}")
            raise
    
    async def list_tasks(
        self,
        skip: int = 0,
        limit: int = 10,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        category_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> tuple[List[TaskRead], int]:
        """
        List tasks with filtering and pagination.
        """
        try:
            # Build query with filters
            query = """
                SELECT t.*, c.name as category_name
                FROM tasks t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE 1=1
            """
            params = []
            
            if priority:
                query += " AND t.priority = ?"
                params.append(priority)
            
            if status:
                query += " AND t.status = ?"
                params.append(status)
            
            if category_id:
                query += " AND t.category_id = ?"
                params.append(category_id)
            
            if search:
                query += " AND (t.title LIKE ? OR t.description LIKE ?)"
                search_term = f"%{search}%"
                params.extend([search_term, search_term])
            
            # Count total for pagination
            count_query = query.replace("SELECT t.*, c.name as category_name", "SELECT COUNT(*)")
            cursor = await self.db.execute(count_query, params)
            total = (await cursor.fetchone())[0]
            
            # Get paginated results
            query += " ORDER BY t.created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, skip])
            
            cursor = await self.db.execute(query, params)
            rows = await cursor.fetchall()
            
            tasks = [self._row_to_task_read(row) for row in rows]
            
            return tasks, total
            
        except Exception as e:
            logger.error(f"Failed to list tasks: {e}")
            raise
    
    async def update_task(self, task_id: int, task_update: TaskUpdate) -> Optional[TaskRead]:
        """
        Update an existing task.
        """
        try:
            # Check if task exists
            existing_task = await self.get_task(task_id)
            if not existing_task:
                return None
            
            # Build update query
            update_fields = []
            params = []
            
            if task_update.title is not None:
                update_fields.append("title = ?")
                params.append(task_update.title)
            
            if task_update.description is not None:
                update_fields.append("description = ?")
                params.append(task_update.description)
            
            if task_update.priority is not None:
                update_fields.append("priority = ?")
                params.append(task_update.priority.value)
            
            if task_update.status is not None:
                update_fields.append("status = ?")
                params.append(task_update.status.value)
                
                # Set completed timestamp when status becomes completed
                if task_update.status == Status.COMPLETED:
                    update_fields.append("completed_at = ?")
                    params.append(datetime.now())
            
            if task_update.category_id is not None:
                update_fields.append("category_id = ?")
                params.append(task_update.category_id)
            
            if task_update.due_date is not None:
                update_fields.append("due_date = ?")
                params.append(task_update.due_date)
            
            if task_update.estimated_hours is not None:
                update_fields.append("estimated_hours = ?")
                params.append(task_update.estimated_hours)
            
            if task_update.actual_hours is not None:
                update_fields.append("actual_hours = ?")
                params.append(task_update.actual_hours)
            
            if not update_fields:
                return existing_task
            
            # Update task
            query = f"""
                UPDATE tasks 
                SET {', '.join(update_fields)}
                WHERE id = ?
            """
            params.append(task_id)
            
            await self.db.execute(query, params)
            
            # Update tags if provided
            if task_update.tags is not None:
                await self._update_task_tags(task_id, task_update.tags)
            
            # Update dependencies if provided
            if task_update.depends_on is not None:
                await self._update_task_dependencies(task_id, task_update.depends_on)
            
            # Get updated task
            updated_task = await self.get_task(task_id)
            
            logger.info(f"Task updated successfully: {task_id}")
            return updated_task
            
        except Exception as e:
            logger.error(f"Failed to update task: {e}")
            raise
    
    async def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by ID.
        """
        try:
            cursor = await self.db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            deleted = cursor.rowcount > 0
            
            if deleted:
                logger.info(f"Task deleted successfully: {task_id}")
            else:
                logger.warning(f"Task not found for deletion: {task_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to delete task: {e}")
            raise
    
    async def get_task_analytics(self) -> TaskAnalyticsResponse:
        """
        Get comprehensive task analytics.
        """
        try:
            # Basic statistics
            total_tasks = await self._get_count("SELECT COUNT(*) FROM tasks")
            completed_tasks = await self._get_count(
                "SELECT COUNT(*) FROM tasks WHERE status = ?", (Status.COMPLETED.value,)
            )
            pending_tasks = await self._get_count(
                "SELECT COUNT(*) FROM tasks WHERE status = ?", (Status.PENDING.value,)
            )
            in_progress_tasks = await self._get_count(
                "SELECT COUNT(*) FROM tasks WHERE status = ?", (Status.IN_PROGRESS.value,)
            )
            overdue_tasks = await self._get_count(
                "SELECT COUNT(*) FROM tasks WHERE due_date < ? AND status != ?",
                (date.today(), Status.COMPLETED.value)
            )
            
            # Calculate metrics
            completed_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Tasks by priority
            tasks_by_priority = await self._get_count_by_field("priority")
            
            # Tasks by status
            tasks_by_status = await self._get_count_by_field("status")
            
            # Tasks by category
            tasks_by_category = await self._get_count_by_field("category_id", "category_name")
            
            # Productivity trend (last 7 days)
            productivity_trend = await self._get_productivity_trend()
            
            # Top priority tasks
            top_priority_tasks = await self.list_tasks(
                limit=5, priority=Priority.URGENT.value
            )
            
            # Recent completed tasks
            recent_completed_tasks = await self.list_tasks(
                limit=5, status=Status.COMPLETED.value
            )
            
            # Upcoming due tasks
            upcoming_due_tasks = await self.list_tasks(
                limit=5, search="due_date"
            )
            
            # Calculate productivity score
            productivity_score = await self._calculate_productivity_score()
            
            # Get AI recommendations
            recommendations = await self._get_ai_recommendations()
            
            analytics = TaskAnalytics(
                total_tasks=total_tasks,
                completed_tasks=completed_tasks,
                pending_tasks=pending_tasks,
                in_progress_tasks=in_progress_tasks,
                overdue_tasks=overdue_tasks,
                completed_percentage=completed_percentage,
                average_completion_time=await self._get_average_completion_time(),
                tasks_by_priority=tasks_by_priority,
                tasks_by_status=tasks_by_status,
                tasks_by_category=tasks_by_category,
                productivity_trend=productivity_trend,
            )
            
            return TaskAnalyticsResponse(
                overview=analytics,
                top_priority_tasks=top_priority_tasks[0],
                recent_completed_tasks=recent_completed_tasks[0],
                upcoming_due_tasks=upcoming_due_tasks[0],
                productivity_score=productivity_score,
                recommendations=recommendations,
            )
            
        except Exception as e:
            logger.error(f"Failed to get task analytics: {e}")
            raise
    
    async def prioritize_tasks(self) -> int:
        """
        AI-powered task prioritization.
        """
        try:
            # Get tasks that need prioritization
            cursor = await self.db.execute("""
                SELECT id, title, description, due_date, estimated_hours
                FROM tasks
                WHERE priority = ? AND status = ?
                ORDER BY due_date ASC, created_at ASC
            """, (Priority.MEDIUM.value, Status.PENDING.value))
            
            tasks = await cursor.fetchall()
            prioritized_count = 0
            
            for task in tasks:
                task_id, title, description, due_date, estimated_hours = task
                
                # Simple AI logic for prioritization
                new_priority = self._calculate_priority(
                    title, description, due_date, estimated_hours
                )
                
                if new_priority != Priority.MEDIUM:
                    await self.db.execute(
                        "UPDATE tasks SET priority = ? WHERE id = ?",
                        (new_priority.value, task_id)
                    )
                    prioritized_count += 1
            
            await self.db.commit()
            logger.info(f"Prioritized {prioritized_count} tasks")
            return prioritized_count
            
        except Exception as e:
            logger.error(f"Failed to prioritize tasks: {e}")
            raise
    
    async def suggest_tasks(self) -> List[TaskSuggestion]:
        """
        AI-powered task suggestions.
        """
        try:
            # Get recent completed tasks for pattern analysis
            cursor = await self.db.execute("""
                SELECT title, description, category_id, estimated_hours
                FROM tasks
                WHERE status = ? AND created_at > ?
                ORDER BY created_at DESC
                LIMIT 10
            """, (Status.COMPLETED.value, datetime.now() - timedelta(days=30)))
            
            completed_tasks = await cursor.fetchall()
            
            # Analyze patterns and generate suggestions
            suggestions = []
            
            # Suggest recurring tasks based on patterns
            if completed_tasks:
                suggestions.extend(await self._suggest_recurring_tasks(completed_tasks))
            
            # Suggest tasks based on overdue items
            overdue_suggestions = await self._suggest_overdue_tasks()
            suggestions.extend(overdue_suggestions)
            
            # Suggest tasks based on capacity
            capacity_suggestions = await self._suggest_capacity_based_tasks()
            suggestions.extend(capacity_suggestions)
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Failed to generate task suggestions: {e}")
            raise
    
    def _row_to_task_read(self, row) -> TaskRead:
        """Convert database row to TaskRead model."""
        return TaskRead(
            id=row['id'],
            title=row['title'],
            description=row['description'],
            priority=Priority(row['priority']),
            status=Status(row['status']),
            category_id=row['category_id'],
            due_date=row['due_date'],
            estimated_hours=row['estimated_hours'],
            actual_hours=row['actual_hours'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            completed_at=row['completed_at'],
            category_name=row['category_name'],
        )
    
    async def _update_task_tags(self, task_id: int, tags: List[str]) -> None:
        """Update task tags."""
        await self.db.execute("DELETE FROM task_tags WHERE task_id = ?", (task_id,))
        if tags:
            await self.db.executemany(
                "INSERT INTO task_tags (task_id, tag) VALUES (?, ?)",
                [(task_id, tag) for tag in tags]
            )
    
    async def _update_task_dependencies(self, task_id: int, dependencies: List[int]) -> None:
        """Update task dependencies."""
        await self.db.execute("DELETE FROM task_dependencies WHERE task_id = ?", (task_id,))
        if dependencies:
            await self.db.executemany(
                "INSERT INTO task_dependencies (task_id, depends_on_id) VALUES (?, ?)",
                [(task_id, dep_id) for dep_id in dependencies]
            )
    
    async def _get_count(self, query: str, params: tuple = None) -> int:
        """Get count from database."""
        cursor = await self.db.execute(query, params or ())
        return (await cursor.fetchone())[0]
    
    async def _get_count_by_field(self, field: str, name_field: str = None) -> Dict[str, int]:
        """Get counts grouped by a field."""
        query = f"SELECT {field}, COUNT(*) as count FROM tasks GROUP BY {field}"
        if name_field:
            query = f"SELECT t.{field}, c.{name_field} as name, COUNT(*) as count FROM tasks t LEFT JOIN categories c ON t.{field} = c.id GROUP BY t.{field}, c.{name_field}"
        
        cursor = await self.db.execute(query)
        rows = await cursor.fetchall()
        
        if name_field:
            return {row['name'] or 'Uncategorized': row['count'] for row in rows}
        else:
            return {row[field] or 'Uncategorized': row['count'] for row in rows}
    
    async def _get_productivity_trend(self) -> List[Dict[str, Any]]:
        """Get productivity trend for the last 7 days."""
        trend = []
        for i in range(7):
            date_str = (date.today() - timedelta(days=i)).isoformat()
            completed = await self._get_count(
                "SELECT COUNT(*) FROM tasks WHERE completed_at >= ? AND completed_at < ?",
                (f"{date_str} 00:00:00", f"{date_str} 23:59:59")
            )
            trend.append({
                "date": date_str,
                "completed": completed,
                "productivity": completed / 10  # Normalize to 0-1 scale
            })
        return trend
    
    async def _calculate_productivity_score(self) -> float:
        """Calculate overall productivity score (0.0 to 1.0)."""
        total_tasks = await self._get_count("SELECT COUNT(*) FROM tasks")
        if total_tasks == 0:
            return 0.0
        
        completed_tasks = await self._get_count(
            "SELECT COUNT(*) FROM tasks WHERE status = ?", (Status.COMPLETED.value,)
        )
        
        # Calculate weighted score
        completion_rate = completed_tasks / total_tasks
        on_time_rate = await self._get_on_time_completion_rate()
        
        return (completion_rate * 0.7) + (on_time_rate * 0.3)
    
    async def _get_on_time_completion_rate(self) -> float:
        """Calculate on-time completion rate."""
        total_completed = await self._get_count(
            "SELECT COUNT(*) FROM tasks WHERE status = ?", (Status.COMPLETED.value,)
        )
        if total_completed == 0:
            return 0.0
        
        on_time_completed = await self._get_count(
            "SELECT COUNT(*) FROM tasks WHERE status = ? AND (due_date IS NULL OR due_date >= completed_at)",
            (Status.COMPLETED.value,)
        )
        
        return on_time_completed / total_completed
    
    async def _get_average_completion_time(self) -> float:
        """Calculate average completion time in days."""
        cursor = await self.db.execute("""
            SELECT AVG(julianday(completed_at) - julianday(created_at)) as avg_days
            FROM tasks
            WHERE status = ? AND completed_at IS NOT NULL
        """, (Status.COMPLETED.value,))
        
        result = await cursor.fetchone()
        return result[0] or 0.0
    
    async def _get_ai_recommendations(self) -> List[str]:
        """Generate AI-based recommendations."""
        recommendations = []
        
        # Check for overdue tasks
        overdue_count = await self._get_count(
            "SELECT COUNT(*) FROM tasks WHERE due_date < ? AND status != ?",
            (date.today(), Status.COMPLETED.value)
        )
        
        if overdue_count > 0:
            recommendations.append(f"You have {overdue_count} overdue tasks that need attention.")
        
        # Check for tasks without due dates
        no_due_date_count = await self._get_count(
            "SELECT COUNT(*) FROM tasks WHERE due_date IS NULL AND status = ?",
            (Status.PENDING.value,)
        )
        
        if no_due_date_count > 0:
            recommendations.append(f"Consider adding due dates to {no_due_date_count} pending tasks.")
        
        # Check for high-priority tasks
        high_priority_count = await self._get_count(
            "SELECT COUNT(*) FROM tasks WHERE priority = ? AND status = ?",
            (Priority.HIGH.value, Status.PENDING.value)
        )
        
        if high_priority_count > 0:
            recommendations.append(f"You have {high_priority_count} high-priority tasks to work on.")
        
        return recommendations
    
    def _calculate_priority(
        self, title: str, description: str, due_date: date, estimated_hours: int
    ) -> Priority:
        """Calculate task priority based on various factors."""
        
        # Check if task is overdue or due soon
        if due_date:
            days_until_due = (due_date - date.today()).days
            if days_until_due < 0:
                return Priority.URGENT
            elif days_until_due <= 2:
                return Priority.HIGH
        
        # Check for urgent keywords in title/description
        urgent_keywords = ['urgent', 'critical', 'asap', 'immediately', 'deadline']
        text_lower = (title + ' ' + description).lower()
        if any(keyword in text_lower for keyword in urgent_keywords):
            return Priority.HIGH
        
        # Check for time complexity
        if estimated_hours and estimated_hours > 8:
            return Priority.LOW
        
        # Default to medium
        return Priority.MEDIUM
    
    async def _suggest_recurring_tasks(self, completed_tasks: List) -> List[TaskSuggestion]:
        """Suggest recurring tasks based on completed patterns."""
        suggestions = []
        
        # Simple pattern detection - suggest similar tasks
        for task in completed_tasks[:3]:  # Only analyze recent tasks
            if "meeting" in task['title'].lower():
                suggestions.append(TaskSuggestion(
                    title="Schedule follow-up meeting",
                    description="Follow up on previous meeting outcomes",
                    priority=Priority.MEDIUM,
                    estimated_hours=1,
                    confidence_score=0.8,
                    reasoning="Based on recent meeting completion pattern"
                ))
        
        return suggestions
    
    async def _suggest_overdue_tasks(self) -> List[TaskSuggestion]:
        """Suggest tasks based on overdue items."""
        cursor = await self.db.execute("""
            SELECT title, description, due_date
            FROM tasks
            WHERE due_date < ? AND status = ?
            ORDER BY due_date ASC
            LIMIT 3
        """, (date.today(), Status.PENDING.value))
        
        overdue_tasks = await cursor.fetchall()
        suggestions = []
        
        for task in overdue_tasks:
            suggestions.append(TaskSuggestion(
                title=f"Urgent: {task['title']}",
                description=f"This task was due on {task['due_date']}. Address immediately.",
                priority=Priority.URGENT,
                estimated_hours=task['description'].count(' ') * 0.1 if task['description'] else 1,
                confidence_score=0.9,
                reasoning="Task is overdue and requires immediate attention"
            ))
        
        return suggestions
    
    async def _suggest_capacity_based_tasks(self) -> List[TaskSuggestion]:
        """Suggest tasks based on current capacity."""
        # Get current week's tasks
        week_start = date.today() - timedelta(days=date.today().weekday())
        week_end = week_start + timedelta(days=6)
        
        cursor = await self.db.execute("""
            SELECT COUNT(*) as count
            FROM tasks
            WHERE created_at >= ? AND created_at <= ?
            AND status IN (?, ?)
        """, (week_start, week_end, Status.PENDING.value, Status.IN_PROGRESS.value))
        
        current_tasks = (await cursor.fetchone())[0]
        
        # Suggest small tasks if current load is low
        if current_tasks < 5:
            suggestions = [TaskSuggestion(
                title="Review and organize task list",
                description="Clean up and organize your current task list",
                priority=Priority.LOW,
                estimated_hours=0.5,
                confidence_score=0.7,
                reasoning="Light workload detected, good time for organization"
            )]
        else:
            suggestions = []
        
        return suggestions
    
    async def _suggest_priority_improvements(self, task: TaskRead) -> None:
        """Suggest priority improvements for a task."""
        # This would integrate with OpenAI API in a real implementation
        pass