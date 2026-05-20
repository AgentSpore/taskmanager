"""
Analytics service for TaskManager.

Provides business intelligence, reporting, and insights for task management.
"""

import time
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from loguru import logger
from collections import defaultdict

from ..core.database import get_db
from ..schemas.task import TaskAnalytics, TaskAnalyticsResponse
from ..schemas.category import CategoryAnalytics
from ..schemas.team import TeamAnalytics


class AnalyticsService:
    """
    Service for analytics and reporting functionality.
    """
    
    def __init__(self, db):
        self.db = db
    
    async def get_task_analytics(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> TaskAnalytics:
        """
        Get comprehensive task analytics.
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Basic statistics
            total_tasks = await self._get_tasks_count(start_date, end_date)
            completed_tasks = await self._get_completed_tasks_count(start_date, end_date)
            pending_tasks = await self._get_pending_tasks_count(start_date, end_date)
            in_progress_tasks = await self._get_in_progress_tasks_count(start_date, end_date)
            overdue_tasks = await self._get_overdue_tasks_count(start_date, end_date)
            
            # Calculate metrics
            completed_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Tasks by priority
            tasks_by_priority = await self._get_tasks_by_priority(start_date, end_date)
            
            # Tasks by status
            tasks_by_status = await self._get_tasks_by_status(start_date, end_date)
            
            # Tasks by category
            tasks_by_category = await self._get_tasks_by_category(start_date, end_date)
            
            # Productivity trend
            productivity_trend = await self._get_productivity_trend(start_date, end_date)
            
            # Average completion time
            average_completion_time = await self._get_average_completion_time(start_date, end_date)
            
            return TaskAnalytics(
                total_tasks=total_tasks,
                completed_tasks=completed_tasks,
                pending_tasks=pending_tasks,
                in_progress_tasks=in_progress_tasks,
                overdue_tasks=overdue_tasks,
                completed_percentage=completed_percentage,
                average_completion_time=average_completion_time,
                tasks_by_priority=tasks_by_priority,
                tasks_by_status=tasks_by_status,
                tasks_by_category=tasks_by_category,
                productivity_trend=productivity_trend,
            )
            
        except Exception as e:
            logger.error(f"Failed to get task analytics: {e}")
            raise
    
    async def get_category_analytics(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> CategoryAnalytics:
        """
        Get category analytics.
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Basic statistics
            total_categories = await self._get_categories_count()
            total_tasks = await self._get_tasks_count(start_date, end_date)
            
            # Calculate metrics
            average_tasks_per_category = total_tasks / total_categories if total_categories > 0 else 0
            
            # Categories by task count
            categories_by_task_count = await self._get_categories_by_task_count(start_date, end_date)
            
            # Most and least active categories
            most_active_category = max(categories_by_task_count, key=lambda x: x['count']) if categories_by_task_count else None
            least_active_category = min(categories_by_task_count, key=lambda x: x['count']) if categories_by_task_count else None
            
            return CategoryAnalytics(
                total_categories=total_categories,
                total_tasks=total_tasks,
                average_tasks_per_category=average_tasks_per_category,
                categories_by_task_count=categories_by_task_count,
                most_active_category=most_active_category,
                least_active_category=least_active_category,
            )
            
        except Exception as e:
            logger.error(f"Failed to get category analytics: {e}")
            raise
    
    async def get_team_analytics(self, team_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> TeamAnalytics:
        """
        Get team analytics.
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Basic statistics
            total_teams = await self._get_teams_count()
            total_members = await self._get_team_members_count(team_id)
            
            # Calculate metrics
            average_members_per_team = total_members / total_teams if total_teams > 0 else 0
            
            # Teams by member count
            teams_by_member_count = await self._get_teams_by_member_count()
            
            # Team productivity scores
            team_productivity_scores = await self._get_team_productivity_scores(team_id, start_date, end_date)
            
            # Most active team
            most_active_team = await self._get_most_active_team(start_date, end_date)
            
            return TeamAnalytics(
                total_teams=total_teams,
                total_members=total_members,
                average_members_per_team=average_members_per_team,
                teams_by_member_count=teams_by_member_count,
                most_active_team=most_active_team,
                team_productivity_scores=team_productivity_scores,
            )
            
        except Exception as e:
            logger.error(f"Failed to get team analytics: {e}")
            raise
    
    async def get_productivity_report(self, user_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Get detailed productivity report for a user.
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Basic metrics
            total_tasks = await self._get_user_tasks_count(user_id, start_date, end_date)
            completed_tasks = await self._get_user_completed_tasks_count(user_id, start_date, end_date)
            
            # Productivity metrics
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            average_completion_time = await self._get_user_average_completion_time(user_id, start_date, end_date)
            
            # Daily productivity trend
            daily_productivity = await self._get_user_daily_productivity(user_id, start_date, end_date)
            
            # Task distribution by priority and status
            priority_distribution = await self._get_user_tasks_by_priority(user_id, start_date, end_date)
            status_distribution = await self._get_user_tasks_by_status(user_id, start_date, end_date)
            
            # Performance trends
            performance_trend = await self._get_user_performance_trend(user_id, start_date, end_date)
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "total_days": (end_date - start_date).days
                },
                "overview": {
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks,
                    "completion_rate": completion_rate,
                    "average_completion_time": average_completion_time
                },
                "daily_productivity": daily_productivity,
                "priority_distribution": priority_distribution,
                "status_distribution": status_distribution,
                "performance_trend": performance_trend,
                "recommendations": await self._get_user_productivity_recommendations(user_id, start_date, end_date)
            }
            
        except Exception as e:
            logger.error(f"Failed to get productivity report: {e}")
            raise
    
    async def get_project_health_metrics(self, project_id: int) -> Dict[str, Any]:
        """
        Get project health metrics.
        """
        try:
            # Project completion metrics
            completion_rate = await self._get_project_completion_rate(project_id)
            
            # On-time delivery rate
            on_time_rate = await self._get_project_on_time_rate(project_id)
            
            # Team velocity
            team_velocity = await self._get_team_velocity(project_id)
            
            # Risk assessment
            risk_assessment = await self._assess_project_risks(project_id)
            
            # Burndown chart data
            burndown_data = await self._get_burndown_data(project_id)
            
            return {
                "completion_rate": completion_rate,
                "on_time_rate": on_time_rate,
                "team_velocity": team_velocity,
                "risk_assessment": risk_assessment,
                "burndown_data": burndown_data,
                "overall_health": self._calculate_overall_health(completion_rate, on_time_rate, team_velocity)
            }
            
        except Exception as e:
            logger.error(f"Failed to get project health metrics: {e}")
            raise
    
    async def generate_insights(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        Generate actionable insights from data.
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            insights = []
            
            # Task completion insights
            completion_insights = await self._analyze_completion_patterns(start_date, end_date)
            insights.extend(completion_insights)
            
            # Priority insights
            priority_insights = await self._analyze_priority_patterns(start_date, end_date)
            insights.extend(priority_insights)
            
            # Time-based insights
            time_insights = await self._analyze_time_patterns(start_date, end_date)
            insights.extend(time_insights)
            
            # Team insights
            team_insights = await self._analyze_team_patterns(start_date, end_date)
            insights.extend(team_insights)
            
            # Category insights
            category_insights = await self._analyze_category_patterns(start_date, end_date)
            insights.extend(category_insights)
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            raise
    
    async def export_analytics(self, export_format: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Export analytics data in various formats.
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Get all analytics data
            task_analytics = await self.get_task_analytics(start_date, end_date)
            category_analytics = await self.get_category_analytics(start_date, end_date)
            insights = await self.generate_insights(start_date, end_date)
            
            export_data = {
                "metadata": {
                    "export_date": datetime.now().isoformat(),
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "format": export_format
                },
                "task_analytics": task_analytics.dict() if hasattr(task_analytics, 'dict') else task_analytics,
                "category_analytics": category_analytics.dict() if hasattr(category_analytics, 'dict') else category_analytics,
                "insights": insights
            }
            
            # Format based on requested format
            if export_format.lower() == "json":
                return export_data
            elif export_format.lower() == "csv":
                return await self._convert_to_csv(export_data)
            elif export_format.lower() == "pdf":
                return await self._convert_to_pdf(export_data)
            else:
                raise ValueError(f"Unsupported export format: {export_format}")
            
        except Exception as e:
            logger.error(f"Failed to export analytics: {e}")
            raise
    
    # Helper methods for database queries
    async def _get_tasks_count(self, start_date: date, end_date: date) -> int:
        """Get total tasks count for date range."""
        cursor = await self.db.execute("""
            SELECT COUNT(*) FROM tasks 
            WHERE created_at BETWEEN ? AND ?
        """, (start_date, end_date))
        return (await cursor.fetchone())[0]
    
    async def _get_completed_tasks_count(self, start_date: date, end_date: date) -> int:
        """Get completed tasks count for date range."""
        cursor = await self.db.execute("""
            SELECT COUNT(*) FROM tasks 
            WHERE status = 'completed' AND completed_at BETWEEN ? AND ?
        """, (start_date, end_date))
        return (await cursor.fetchone())[0]
    
    async def _get_pending_tasks_count(self, start_date: date, end_date: date) -> int:
        """Get pending tasks count for date range."""
        cursor = await self.db.execute("""
            SELECT COUNT(*) FROM tasks 
            WHERE status = 'pending' AND created_at BETWEEN ? AND ?
        """, (start_date, end_date))
        return (await cursor.fetchone())[0]
    
    async def _get_in_progress_tasks_count(self, start_date: date, end_date: date) -> int:
        """Get in-progress tasks count for date range."""
        cursor = await self.db.execute("""
            SELECT COUNT(*) FROM tasks 
            WHERE status = 'in_progress' AND created_at BETWEEN ? AND ?
        """, (start_date, end_date))
        return (await cursor.fetchone())[0]
    
    async def _get_overdue_tasks_count(self, start_date: date, end_date: date) -> int:
        """Get overdue tasks count for date range."""
        cursor = await self.db.execute("""
            SELECT COUNT(*) FROM tasks 
            WHERE due_date < ? AND status != 'completed' AND created_at BETWEEN ? AND ?
        """, (date.today(), start_date, end_date))
        return (await cursor.fetchone())[0]
    
    async def _get_tasks_by_priority(self, start_date: date, end_date: date) -> Dict[str, int]:
        """Get tasks count by priority for date range."""
        cursor = await self.db.execute("""
            SELECT priority, COUNT(*) FROM tasks 
            WHERE created_at BETWEEN ? AND ?
            GROUP BY priority
        """, (start_date, end_date))
        return {row[0]: row[1] for row in await cursor.fetchall()}
    
    async def _get_tasks_by_status(self, start_date: date, end_date: date) -> Dict[str, int]:
        """Get tasks count by status for date range."""
        cursor = await self.db.execute("""
            SELECT status, COUNT(*) FROM tasks 
            WHERE created_at BETWEEN ? AND ?
            GROUP BY status
        """, (start_date, end_date))
        return {row[0]: row[1] for row in await cursor.fetchall()}
    
    async def _get_tasks_by_category(self, start_date: date, end_date: date) -> Dict[str, int]:
        """Get tasks count by category for date range."""
        cursor = await self.db.execute("""
            SELECT c.name, COUNT(t.id) 
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.created_at BETWEEN ? AND ?
            GROUP BY c.name
        """, (start_date, end_date))
        return {row[0]: row[1] for row in await cursor.fetchall()}
    
    async def _get_productivity_trend(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get productivity trend for date range."""
        trend = []
        current_date = start_date
        
        while current_date <= end_date:
            cursor = await self.db.execute("""
                SELECT COUNT(*) FROM tasks 
                WHERE completed_at >= ? AND completed_at < ?
            """, (current_date, current_date + timedelta(days=1)))
            
            completed = (await cursor.fetchone())[0]
            trend.append({
                "date": current_date.isoformat(),
                "completed": completed,
                "productivity": completed / 10  # Normalize to 0-1 scale
            })
            
            current_date += timedelta(days=1)
        
        return trend
    
    async def _get_average_completion_time(self, start_date: date, end_date: date) -> float:
        """Get average completion time for date range."""
        cursor = await self.db.execute("""
            SELECT AVG(julianday(completed_at) - julianday(created_at)) as avg_days
            FROM tasks
            WHERE status = 'completed' AND completed_at BETWEEN ? AND ? AND completed_at IS NOT NULL
        """, (start_date, end_date))
        
        result = await cursor.fetchone()
        return result[0] or 0.0
    
    # Additional helper methods would be implemented here...
    async def _get_categories_count(self) -> int:
        """Get total categories count."""
        cursor = await self.db.execute("SELECT COUNT(*) FROM categories")
        return (await cursor.fetchone())[0]
    
    async def _get_categories_by_task_count(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get categories by task count for date range."""
        cursor = await self.db.execute("""
            SELECT c.name, COUNT(t.id) as count
            FROM categories c
            LEFT JOIN tasks t ON c.id = t.category_id AND t.created_at BETWEEN ? AND ?
            GROUP BY c.name
            ORDER BY count DESC
        """, (start_date, end_date))
        return [{"name": row[0], "count": row[1]} for row in await cursor.fetchall()]
    
    async def _get_teams_count(self) -> int:
        """Get total teams count."""
        cursor = await self.db.execute("SELECT COUNT(*) FROM teams")
        return (await cursor.fetchone())[0]
    
    async def _get_team_members_count(self, team_id: int) -> int:
        """Get team members count."""
        cursor = await self.db.execute("""
            SELECT COUNT(*) FROM team_members 
            WHERE team_id = ?
        """, (team_id,))
        return (await cursor.fetchone())[0]
    
    async def _get_teams_by_member_count(self) -> List[Dict[str, Any]]:
        """Get teams by member count."""
        cursor = await self.db.execute("""
            SELECT t.name, COUNT(tm.user_id) as member_count
            FROM teams t
            LEFT JOIN team_members tm ON t.id = tm.team_id
            GROUP BY t.name
            ORDER BY member_count DESC
        """)
        return [{"name": row[0], "member_count": row[1]} for row in await cursor.fetchall()]
    
    async def _get_team_productivity_scores(self, team_id: int, start_date: date, end_date: date) -> Dict[int, float]:
        """Get team productivity scores."""
        cursor = await self.db.execute("""
            SELECT tm.user_id, COUNT(t.id) as completed_tasks
            FROM team_members tm
            LEFT JOIN tasks t ON tm.user_id = t.assigned_to AND t.status = 'completed' AND t.completed_at BETWEEN ? AND ?
            WHERE tm.team_id = ?
            GROUP BY tm.user_id
        """, (start_date, end_date, team_id))
        
        return {row[0]: row[1] / 10 for row in await cursor.fetchall()}
    
    async def _get_most_active_team(self, start_date: date, end_date: date) -> Optional[Dict[str, Any]]:
        """Get most active team for date range."""
        cursor = await self.db.execute("""
            SELECT t.name, COUNT(ta.id) as task_count
            FROM teams t
            LEFT JOIN tasks ta ON t.id = ta.created_by AND ta.created_at BETWEEN ? AND ?
            GROUP BY t.name
            ORDER BY task_count DESC
            LIMIT 1
        """, (start_date, end_date))
        
        row = await cursor.fetchone()
        return {"name": row[0], "task_count": row[1]} if row else None
    
    async def _get_user_tasks_count(self, user_id: int, start_date: date, end_date: date) -> int:
        """Get user tasks count for date range."""
        cursor = await self.db.execute("""
            SELECT COUNT(*) FROM tasks 
            WHERE (created_by = ? OR assigned_to = ?) AND created_at BETWEEN ? AND ?
        """, (user_id, user_id, start_date, end_date))
        return (await cursor.fetchone())[0]
    
    async def _get_user_completed_tasks_count(self, user_id: int, start_date: date, end_date: date) -> int:
        """Get user completed tasks count for date range."""
        cursor = await self.db.execute("""
            SELECT COUNT(*) FROM tasks 
            WHERE (created_by = ? OR assigned_to = ?) AND status = 'completed' AND completed_at BETWEEN ? AND ?
        """, (user_id, user_id, start_date, end_date))
        return (await cursor.fetchone())[0]
    
    async def _get_user_average_completion_time(self, user_id: int, start_date: date, end_date: date) -> float:
        """Get user average completion time for date range."""
        cursor = await self.db.execute("""
            SELECT AVG(julianday(completed_at) - julianday(created_at)) as avg_days
            FROM tasks
            WHERE (created_by = ? OR assigned_to = ?) AND status = 'completed' AND completed_at BETWEEN ? AND ? AND completed_at IS NOT NULL
        """, (user_id, user_id, start_date, end_date))
        
        result = await cursor.fetchone()
        return result[0] or 0.0
    
    async def _get_user_daily_productivity(self, user_id: int, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get user daily productivity for date range."""
        productivity = []
        current_date = start_date
        
        while current_date <= end_date:
            cursor = await self.db.execute("""
                SELECT COUNT(*) FROM tasks 
                WHERE (created_by = ? OR assigned_to = ?) AND completed_at >= ? AND completed_at < ?
            """, (user_id, user_id, current_date, current_date + timedelta(days=1)))
            
            completed = (await cursor.fetchone())[0]
            productivity.append({
                "date": current_date.isoformat(),
                "completed": completed,
                "productivity": completed / 5  # Normalize to 0-1 scale
            })
            
            current_date += timedelta(days=1)
        
        return productivity
    
    async def _get_user_tasks_by_priority(self, user_id: int, start_date: date, end_date: date) -> Dict[str, int]:
        """Get user tasks count by priority for date range."""
        cursor = await self.db.execute("""
            SELECT priority, COUNT(*) FROM tasks 
            WHERE (created_by = ? OR assigned_to = ?) AND created_at BETWEEN ? AND ?
            GROUP BY priority
        """, (user_id, user_id, start_date, end_date))
        return {row[0]: row[1] for row in await cursor.fetchall()}
    
    async def _get_user_tasks_by_status(self, user_id: int, start_date: date, end_date: date) -> Dict[str, int]:
        """Get user tasks count by status for date range."""
        cursor = await self.db.execute("""
            SELECT status, COUNT(*) FROM tasks 
            WHERE (created_by = ? OR assigned_to = ?) AND created_at BETWEEN ? AND ?
            GROUP BY status
        """, (user_id, user_id, start_date, end_date))
        return {row[0]: row[1] for row in await cursor.fetchall()}
    
    async def _get_user_performance_trend(self, user_id: int, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get user performance trend for date range."""
        # This would include more complex metrics in a real implementation
        return await self._get_user_daily_productivity(user_id, start_date, end_date)
    
    async def _get_user_productivity_recommendations(self, user_id: int, start_date: date, end_date: date) -> List[str]:
        """Get user productivity recommendations for date range."""
        recommendations = []
        
        # Check completion rate
        total_tasks = await self._get_user_tasks_count(user_id, start_date, end_date)
        completed_tasks = await self._get_user_completed_tasks_count(user_id, start_date, end_date)
        
        if total_tasks > 0:
            completion_rate = completed_tasks / total_tasks
            if completion_rate < 0.5:
                recommendations.append("Focus on completing existing tasks before starting new ones")
            elif completion_rate > 0.9:
                recommendations.append("You're very productive! Consider taking on more challenging tasks")
        
        # Check task distribution
        priority_dist = await self._get_user_tasks_by_priority(user_id, start_date, end_date)
        high_priority_count = priority_dist.get('high', 0)
        
        if high_priority_count > 5:
            recommendations.append("You have many high-priority tasks. Consider delegating some or breaking them down")
        
        return recommendations
    
    # Additional helper methods for analytics calculations...
    async def _analyze_completion_patterns(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Analyze task completion patterns."""
        patterns = []
        
        # Check for completion trends
        completed_rate = await self._get_completed_tasks_count(start_date, end_date) / await self._get_tasks_count(start_date, end_date)
        
        if completed_rate > 0.8:
            patterns.append({
                "type": "positive",
                "title": "High Completion Rate",
                "description": f"You're completing {completed_rate:.1%} of your tasks",
                "action": "Keep up the great work!"
            })
        elif completed_rate < 0.4:
            patterns.append({
                "type": "warning",
                "title": "Low Completion Rate",
                "description": f"Only {completed_rate:.1%} of tasks are being completed",
                "action": "Review your task prioritization and workload"
            })
        
        return patterns
    
    async def _analyze_priority_patterns(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Analyze task priority patterns."""
        patterns = []
        
        priority_dist = await self._get_tasks_by_priority(start_date, end_date)
        urgent_count = priority_dist.get('urgent', 0)
        total_tasks = sum(priority_dist.values())
        
        if urgent_count > total_tasks * 0.3:
            patterns.append({
                "type": "warning",
                "title": "High Urgent Task Volume",
                "description": f"{urgent_count} out of {total_tasks} tasks are urgent",
                "action": "Review your task management process to reduce last-minute work"
            })
        
        return patterns
    
    async def _analyze_time_patterns(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Analyze time-based patterns."""
        patterns = []
        
        # Check for weekend work
        weekend_tasks = 0
        weekday_tasks = 0
        
        cursor = await self.db.execute("""
            SELECT created_at FROM tasks 
            WHERE created_at BETWEEN ? AND ?
        """, (start_date, end_date))
        
        for row in await cursor.fetchall():
            created_at = row[0]
            if created_at.weekday() >= 5:  # Weekend
                weekend_tasks += 1
            else:
                weekday_tasks += 1
        
        if weekend_tasks > weekday_tasks * 0.2:
            patterns.append({
                "type": "warning",
                "title": "Weekend Work Patterns",
                "description": f"You're working on {weekend_tasks} tasks on weekends",
                "action": "Consider better workload distribution during weekdays"
            })
        
        return patterns
    
    async def _analyze_team_patterns(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Analyze team patterns."""
        patterns = []
        
        # Check team collaboration patterns
        teams_by_member_count = await self._get_teams_by_member_count()
        
        large_teams = [team for team in teams_by_member_count if team['member_count'] > 10]
        if large_teams:
            patterns.append({
                "type": "info",
                "title": "Large Team Structure",
                "description": f"You have {len(large_teams)} teams with more than 10 members",
                "action": "Consider breaking down large teams for better coordination"
            })
        
        return patterns
    
    async def _analyze_category_patterns(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Analyze category patterns."""
        patterns = []
        
        category_dist = await self._get_tasks_by_category(start_date, end_date)
        
        if len(category_dist) > 10:
            patterns.append({
                "type": "info",
                "title": "Many Task Categories",
                "description": f"You have {len(category_dist)} different task categories",
                "action": "Consider consolidating similar categories to reduce complexity"
            })
        
        return patterns
    
    async def _convert_to_csv(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert analytics data to CSV format."""
        # This would implement CSV conversion logic
        return {
            "format": "csv",
            "data": "CSV data would be generated here",
            "filename": "analytics_report.csv"
        }
    
    async def _convert_to_pdf(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert analytics data to PDF format."""
        # This would implement PDF conversion logic
        return {
            "format": "pdf",
            "data": "PDF data would be generated here",
            "filename": "analytics_report.pdf"
        }
    
    def _calculate_overall_health(self, completion_rate: float, on_time_rate: float, team_velocity: float) -> str:
        """Calculate overall project health."""
        health_score = (completion_rate + on_time_rate + team_velocity) / 3
        
        if health_score >= 0.8:
            return "Excellent"
        elif health_score >= 0.6:
            return "Good"
        elif health_score >= 0.4:
            return "Fair"
        else:
            return "Poor"