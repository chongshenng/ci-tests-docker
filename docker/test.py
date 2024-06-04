from testcontainers.compose import DockerCompose, ContainerIsNotRunning
import pytest

COMPOSE_MANIFEST = "compose.yaml"


def test_compose():
    """stream-of-consciousness e2e test"""
    basic = DockerCompose(context=".", compose_file_name=COMPOSE_MANIFEST)
    try:
        # first it does not exist
        containers = basic.get_containers(include_all=True)
        assert len(containers) == 0

        # then we create it and it exists
        basic.start()
        containers = basic.get_containers(include_all=True)
        assert len(containers) == 1
        containers = basic.get_containers()
        assert len(containers) == 1

        # test that get_container returns the same object, value assertions, etc
        from_all = containers[0]
        assert from_all.State == "running"
        assert from_all.Service == "alpine"

        by_name = basic.get_container("alpine")

        assert by_name.Name == from_all.Name
        assert by_name.Service == from_all.Service
        assert by_name.State == from_all.State
        assert by_name.ID == from_all.ID

        assert by_name.ExitCode == 0

        # what if you want to get logs after it crashes:
        basic.stop(down=False)

        with pytest.raises(ContainerIsNotRunning):
            assert basic.get_container("alpine") is None

        # what it looks like after it exits
        stopped = basic.get_container("alpine", include_all=True)
        assert stopped.State == "exited"
    finally:
        basic.stop()
