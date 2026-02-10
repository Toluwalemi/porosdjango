from unittest.mock import MagicMock, patch

import pytest

from porosdjango.cli import TemplateRenderer
from porosdjango.exceptions import TemplateRenderError


def test_render_succeeds():
    """GIVEN a TemplateRenderer with a valid template environment
    WHEN render is called with a valid template name
    THEN the rendered content string is returned
    """
    with patch("porosdjango.cli.Environment") as mock_env_cls:
        mock_template = MagicMock()
        mock_template.render.return_value = "rendered content"
        mock_env_cls.return_value.get_template.return_value = mock_template

        renderer = TemplateRenderer()
        result = renderer.render("test.j2")

        assert result == "rendered content"
        mock_env_cls.return_value.get_template.assert_called_with("test.j2")


def test_render_with_context_variables_succeeds():
    """GIVEN a TemplateRenderer with a valid template environment
    WHEN render is called with context keyword arguments
    THEN the context variables are passed to the template
    """
    with patch("porosdjango.cli.Environment") as mock_env_cls:
        mock_template = MagicMock()
        mock_template.render.return_value = "rendered with vars"
        mock_env_cls.return_value.get_template.return_value = mock_template

        renderer = TemplateRenderer()
        result = renderer.render("test.j2", project_name="myproject")

        assert result == "rendered with vars"
        mock_template.render.assert_called_with(project_name="myproject")


def test_render_with_missing_template_fails():
    """GIVEN a TemplateRenderer with a broken template environment
    WHEN render is called with a missing template name
    THEN a TemplateRenderError is raised
    """
    with patch("porosdjango.cli.Environment") as mock_env_cls:
        mock_env_cls.return_value.get_template.side_effect = Exception(
            "Template missing"
        )

        renderer = TemplateRenderer()
        with pytest.raises(TemplateRenderError, match="Failed to render template"):
            renderer.render("missing.j2")
