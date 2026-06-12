from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.models.categoria import Categoria
from app.models.unidad_medida import UnidadMedida
from app.schemas.categoria_schema import CategoriaCreate
from app.schemas.unidad_medida_schema import UnidadMedidaCreate, UnidadMedidaUpdate
from app.services import categoria_service, unidad_medida_service
from tests.conftest import DummyRepo


def test_unidad_medida_listar_delegates_pagination(unidad):
    uow = SimpleNamespace(unidades_medida=DummyRepo([unidad]))
    result = unidad_medida_service.listar(uow, incluir_eliminadas=True, page=2, size=5)
    assert result == [unidad]
    assert uow.unidades_medida.last_kwargs == {"incluir_eliminadas": True, "page": 2, "size": 5}


def test_unidad_medida_obtener_returns_existing_entity(unidad):
    uow = SimpleNamespace(unidades_medida=DummyRepo([unidad]))
    assert unidad_medida_service.obtener(uow, 1) is unidad


def test_unidad_medida_obtener_deleted_raises_when_not_including_deleted(unidad):
    unidad.deleted_at = datetime.now(timezone.utc)
    uow = SimpleNamespace(unidades_medida=DummyRepo([unidad]))
    with pytest.raises(HTTPException) as exc:
        unidad_medida_service.obtener(uow, 1)
    assert exc.value.status_code == 404


def test_unidad_medida_crear_normalizes_text_values():
    repo = DummyRepo()
    uow = SimpleNamespace(unidades_medida=repo)
    payload = UnidadMedidaCreate(nombre=" Kilogramo ", simbolo=" kg ", tipo=" peso ")
    unidad = unidad_medida_service.crear(uow, payload)
    assert unidad.nombre == "Kilogramo"
    assert unidad.simbolo == "kg"
    assert unidad.tipo == "peso"
    assert repo.created[-1] is unidad


def test_unidad_medida_actualizar_applies_changes_and_activar_reactivates(unidad):
    repo = DummyRepo([unidad])
    uow = SimpleNamespace(unidades_medida=repo)

    payload = UnidadMedidaUpdate(nombre="Unidad actualizada", activo=False)
    updated = unidad_medida_service.actualizar(uow, 1, payload)
    assert updated.nombre == "Unidad actualizada"
    assert updated.activo is False
    assert repo.updated[-1] is updated

    unidad.deleted_at = datetime.now(timezone.utc)
    reactivated = unidad_medida_service.activar(uow, 1)
    assert reactivated.activo is True
    assert reactivated.deleted_at is None
    assert repo.updated[-1] is reactivated


def test_unidad_medida_eliminar_soft_deletes_entity(unidad):
    repo = DummyRepo([unidad])
    uow = SimpleNamespace(unidades_medida=repo)
    unidad_medida_service.eliminar(uow, 1)
    assert unidad.activo is False
    assert unidad.deleted_at is not None
    assert repo.updated[-1] is unidad


def test_categoria_crear_validates_parent_and_duplicate_name(categoria):
    repo = DummyRepo([categoria])
    uow = SimpleNamespace(categorias=repo)
    with pytest.raises(HTTPException) as exc:
        categoria_service.crear(uow, CategoriaCreate(nombre="Bebidas"))
    assert exc.value.status_code == 409


def test_categoria_listar_arbol_builds_parent_child_tree(now_utc):
    padre = Categoria(id=1, nombre="Bebidas", created_at=now_utc, updated_at=now_utc)
    hijo = Categoria(id=2, nombre="Sin gas", parent_id=1, created_at=now_utc, updated_at=now_utc)
    uow = SimpleNamespace(categorias=DummyRepo([padre, hijo]))
    tree = categoria_service.listar_arbol(uow)
    assert len(tree) == 1
    assert tree[0].nombre == "Bebidas"
    assert tree[0].hijos[0].nombre == "Sin gas"
