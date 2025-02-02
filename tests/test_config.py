import pytest
from fastapi import Depends, status

from fastapi_filters.config import ConfigVar


def test_config_var():
    var = ConfigVar("test", default=1)

    assert var.get() == 1

    with var.set(2):
        assert var.get() == 2

    assert var.get() == 1

    with var.set(3) as reset_ctx:
        assert var.get() == 3
        reset_ctx.reset()
        assert var.get() == 1


def test_config_var_double_reset():
    var = ConfigVar("test", default=1)

    reset = var.set(2)
    reset.reset()

    with pytest.raises(ValueError):  # noqa: PT011
        reset.reset()


@pytest.mark.asyncio
async def test_config_var_dependency(app, client):
    var = ConfigVar("test", default=1)

    @app.get("/", dependencies=[Depends(var.dependency(2))])
    async def index():
        assert var.get() == 2

    response = await client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert var.get() == 1
