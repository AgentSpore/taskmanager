"""
Team schemas for TaskManager.

Pydantic models for team data validation and serialization.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class TeamMember(BaseModel):
    """Team member schema."""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: str = "member"
    joined_at: datetime
    
    class Config:
        from_attributes = True


class TeamBase(BaseModel):
    """Base team schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Team name")
    description: Optional[str] = Field(None, max_length=500, description="Team description")


class TeamCreate(TeamBase):
    """Schema for creating new teams."""
    pass


class TeamUpdate(BaseModel):
    """Schema for updating existing teams."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Team name")
    description: Optional[str] = Field(None, max_length=500, description="Team description")


class TeamRead(TeamBase):
    """Schema for reading team data (includes database fields)."""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    member_count: int = Field(0, description="Number of team members")
    members: List[TeamMember] = Field(default_factory=list, description="Team members")
    
    class Config:
        from_attributes = True


class TeamListResponse(BaseModel):
    """Response schema for team list."""
    teams: List[TeamRead]
    total: int


class TeamAnalytics(BaseModel):
    """Analytics data for teams."""
    total_teams: int
    total_members: int
    average_members_per_team: float
    teams_by_member_count: List[Dict[str, Any]]
    most_active_team: Optional[TeamRead] = None
    team_productivity_scores: Dict[int, float]  # team_id: score


class TeamMemberCreate(BaseModel):
    """Schema for adding team members."""
    user_id: int = Field(..., description="User ID to add to team")
    role: str = Field("member", description="Team role")


class TeamMemberUpdate(BaseModel):
    """Schema for updating team member role."""
    role: str = Field(..., description="Team role")


class TeamBulkAddMembers(BaseModel):
    """Schema for bulk adding team members."""
    user_ids: List[int] = Field(..., min_items=1, description="List of user IDs to add")
    role: str = Field("member", description="Default role for new members")


class TeamBulkRemoveMembers(BaseModel):
    """Schema for bulk removing team members."""
    user_ids: List[int] = Field(..., min_items=1, description="List of user IDs to remove")


class TeamImportRequest(BaseModel):
    """Request for team import."""
    data: List[TeamCreate] = Field(..., description="List of teams to import")


class TeamExportRequest(BaseModel):
    """Request for team export."""
    format: str = Field(..., regex="^(csv|json)$", description="Export format")
    include_member_count: bool = Field(True, description="Include member counts")
    include_members: bool = Field(True, description="Include member details")
    filters: Optional[Dict[str, Any]] = Field(None, description="Export filters")


class TeamPermission(BaseModel):
    """Team permission schema."""
    can_create_tasks: bool = True
    can_edit_tasks: bool = False
    can_delete_tasks: bool = False
    can_manage_members: bool = False
    can_view_analytics: bool = False
    can_export_data: bool = False


class TeamRole(BaseModel):
    """Team role definitions."""
    name: str
    permissions: TeamPermission
    description: Optional[str] = None


class TeamRoles(BaseModel):
    """Available team roles."""
    owner: TeamRole = TeamRole(
        name="owner",
        permissions=TeamPermission(
            can_create_tasks=True,
            can_edit_tasks=True,
            can_delete_tasks=True,
            can_manage_members=True,
            can_view_analytics=True,
            can_export_data=True
        ),
        description="Team owner with full permissions"
    )
    
    admin: TeamRole = TeamRole(
        name="admin",
        permissions=TeamPermission(
            can_create_tasks=True,
            can_edit_tasks=True,
            can_delete_tasks=True,
            can_manage_members=True,
            can_view_analytics=True,
            can_export_data=False
        ),
        description="Team administrator with most permissions"
    )
    
    member: TeamRole = TeamRole(
        name="member",
        permissions=TeamPermission(
            can_create_tasks=True,
            can_edit_tasks=True,
            can_delete_tasks=False,
            can_manage_members=False,
            can_view_analytics=False,
            can_export_data=False
        ),
        description="Regular team member"
    )
    
    viewer: TeamRole = TeamRole(
        name="viewer",
        permissions=TeamPermission(
            can_create_tasks=False,
            can_edit_tasks=False,
            can_delete_tasks=False,
            can_manage_members=False,
            can_view_analytics=True,
            can_export_data=False
        ),
        description="Read-only team member"
    )


def get_team_role(role_name: str) -> Optional[TeamRole]:
    """Get team role by name."""
    roles = TeamRoles()
    return getattr(roles, role_name, None)