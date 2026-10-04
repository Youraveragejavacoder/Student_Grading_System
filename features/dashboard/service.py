from features.dashboard.repository import DashboardRepository
from features.dashboard.model import DashboardStats, RolePermissions, UserRole


class UIService:
    def __init__(self, repository: DashboardRepository):
        self.repository = repository

    def get_dashboard_stats(self) -> DashboardStats:
        return self.repository.get_stats()

    def get_permissions_for_role(self, role: UserRole) -> RolePermissions:
        if role == UserRole.ADMIN:
            return RolePermissions(
                role=role,
                can_add_student=True,
                can_update_student=True,
                can_delete_student=True,
                can_add_grade=True,
                can_update_grade=True,
                can_delete_grade=True,
            )
        elif role == UserRole.TEACHER:
            return RolePermissions(
                role=role,
                can_add_student=False,
                can_update_student=False,
                can_delete_student=False,
                can_add_grade=True,
                can_update_grade=True,
                can_delete_grade=False,
            )
        else:
            return RolePermissions(
                role=role,
                can_add_student=False,
                can_update_student=False,
                can_delete_student=False,
                can_add_grade=False,
                can_update_grade=False,
                can_delete_grade=False,
            )
