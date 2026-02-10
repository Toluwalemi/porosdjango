import os

from porosdjango.cli import ProjectScaffold, TemplateRenderer


def test_create_docker_setup_creates_directory_structure_succeeds(
    tmp_path, monkeypatch
):
    """GIVEN a ProjectScaffold with a valid renderer
    WHEN create_docker_setup is called with a project name
    THEN all expected directories are created
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / "myproject").mkdir()
    renderer = TemplateRenderer()
    scaffold = ProjectScaffold(renderer)

    scaffold.create_docker_setup("myproject")

    expected_dirs = [
        os.path.join("infrastructure", "docker", "scripts"),
        os.path.join("infrastructure", "docker", "nginx"),
        os.path.join("infrastructure", "docker", "prometheus"),
        os.path.join("infrastructure", "docker", "alertmanager"),
        os.path.join(
            "infrastructure",
            "docker",
            "grafana",
            "provisioning",
            "datasources",
        ),
        os.path.join(
            "infrastructure",
            "docker",
            "grafana",
            "provisioning",
            "dashboards",
            "json",
        ),
    ]
    for d in expected_dirs:
        assert (tmp_path / d).is_dir(), f"Directory {d} was not created"


def test_create_docker_setup_writes_all_files_succeeds(tmp_path, monkeypatch):
    """GIVEN a ProjectScaffold with a valid renderer
    WHEN create_docker_setup is called with a project name
    THEN all expected files are written
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / "myproject").mkdir()
    renderer = TemplateRenderer()
    scaffold = ProjectScaffold(renderer)

    scaffold.create_docker_setup("myproject")

    expected_files = [
        os.path.join("infrastructure", "docker", "Dockerfile"),
        "docker-compose.yml",
        ".dockerignore",
        ".env.example",
        os.path.join("infrastructure", "docker", "scripts", "dev.sh"),
        os.path.join("infrastructure", "docker", "scripts", "celery_worker.sh"),
        os.path.join("infrastructure", "docker", "scripts", "celery_beat.sh"),
        os.path.join("infrastructure", "docker", "scripts", "flower.sh"),
        os.path.join("infrastructure", "docker", "nginx", "nginx.conf"),
        os.path.join("infrastructure", "docker", "prometheus", "prometheus.yml"),
        os.path.join("infrastructure", "docker", "prometheus", "alert_rules.yml"),
        os.path.join("infrastructure", "docker", "alertmanager", "alertmanager.yml"),
        os.path.join(
            "infrastructure",
            "docker",
            "grafana",
            "provisioning",
            "datasources",
            "datasource.yml",
        ),
        os.path.join(
            "infrastructure",
            "docker",
            "grafana",
            "provisioning",
            "dashboards",
            "dashboard.yml",
        ),
        os.path.join(
            "infrastructure",
            "docker",
            "grafana",
            "provisioning",
            "dashboards",
            "json",
            "django-app.json",
        ),
        os.path.join(
            "infrastructure",
            "docker",
            "grafana",
            "provisioning",
            "dashboards",
            "json",
            "infrastructure.json",
        ),
        os.path.join(
            "infrastructure",
            "docker",
            "grafana",
            "provisioning",
            "dashboards",
            "json",
            "celery.json",
        ),
        os.path.join("myproject", "celery.py"),
        os.path.join("myproject", "__init__.py"),
    ]
    for f in expected_files:
        assert (tmp_path / f).is_file(), f"File {f} was not created"


def test_create_docker_setup_renders_templates_with_project_name_succeeds(
    tmp_path, monkeypatch
):
    """GIVEN a ProjectScaffold with a valid renderer
    WHEN create_docker_setup is called with project name 'myproject'
    THEN rendered files contain 'myproject' instead of 'pywhisperer'
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / "myproject").mkdir()
    renderer = TemplateRenderer()
    scaffold = ProjectScaffold(renderer)

    scaffold.create_docker_setup("myproject")

    compose_content = (tmp_path / "docker-compose.yml").read_text()
    assert "name: myproject" in compose_content
    assert "myproject-network" in compose_content
    assert "pywhisperer" not in compose_content

    env_content = (tmp_path / ".env.example").read_text()
    assert "POSTGRES_DB=myproject" in env_content
    assert "noreply@myproject.local" in env_content

    celery_worker_content = (
        tmp_path / "infrastructure" / "docker" / "scripts" / "celery_worker.sh"
    ).read_text()
    assert "celery -A myproject" in celery_worker_content

    alertmanager_content = (
        tmp_path / "infrastructure" / "docker" / "alertmanager" / "alertmanager.yml"
    ).read_text()
    assert "alertmanager@myproject.local" in alertmanager_content
    assert "alerts@myproject.local" in alertmanager_content


def test_create_docker_setup_preserves_prometheus_template_syntax_succeeds(
    tmp_path, monkeypatch
):
    """GIVEN a ProjectScaffold with a valid renderer
    WHEN create_docker_setup is called
    THEN Prometheus template syntax {{ $labels.job }} is preserved
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / "myproject").mkdir()
    renderer = TemplateRenderer()
    scaffold = ProjectScaffold(renderer)

    scaffold.create_docker_setup("myproject")

    alert_rules = (
        tmp_path / "infrastructure" / "docker" / "prometheus" / "alert_rules.yml"
    ).read_text()
    assert "{{ $labels.job }}" in alert_rules


def test_create_docker_setup_creates_celery_config_succeeds(tmp_path, monkeypatch):
    """GIVEN a ProjectScaffold and a pre-existing project directory
    WHEN create_docker_setup is called
    THEN {project}/celery.py exists with correct Celery app config
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / "myproject").mkdir()

    renderer = TemplateRenderer()
    scaffold = ProjectScaffold(renderer)
    scaffold.create_docker_setup("myproject")

    celery_file = tmp_path / "myproject" / "celery.py"
    assert celery_file.is_file()

    content = celery_file.read_text()
    assert 'Celery("myproject")' in content
    assert '"myproject.settings"' in content
    assert "app.autodiscover_tasks()" in content


def test_create_docker_setup_creates_init_with_celery_succeeds(tmp_path, monkeypatch):
    """GIVEN a ProjectScaffold and a pre-existing project directory
    WHEN create_docker_setup is called
    THEN {project}/__init__.py imports the celery app
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / "myproject").mkdir()

    renderer = TemplateRenderer()
    scaffold = ProjectScaffold(renderer)
    scaffold.create_docker_setup("myproject")

    init_file = tmp_path / "myproject" / "__init__.py"
    assert init_file.is_file()

    content = init_file.read_text()
    assert "from myproject.celery import app as celery_app" in content
    assert '__all__ = ("celery_app",)' in content
