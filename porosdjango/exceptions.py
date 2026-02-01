class PorosDjangoError(Exception):
    """Base exception for all PorosDjango errors."""


class ProjectCreationError(PorosDjangoError):
    """Raised when Django project creation fails."""


class AppCreationError(PorosDjangoError):
    """Raised when Django app creation fails."""


class SettingsUpdateError(PorosDjangoError):
    """Raised when settings.py modification fails."""


class DependencyInstallError(PorosDjangoError):
    """Raised when dependency installation fails."""


class TemplateRenderError(PorosDjangoError):
    """Raised when a Jinja2 template fails to render or write."""


class InvalidAppNameError(PorosDjangoError):
    """Raised when a provided app name is not a valid Python/Django identifier."""
