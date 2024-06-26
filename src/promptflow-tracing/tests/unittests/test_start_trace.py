# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import uuid

import pytest
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from pytest_mock import MockerFixture

import promptflow.tracing._start_trace
from promptflow.tracing import start_trace
from promptflow.tracing._constants import (
    PF_TRACING_SKIP_LOCAL_SETUP_ENVIRON,
    RESOURCE_ATTRIBUTES_SERVICE_NAME,
    ResourceAttributesFieldName,
)


@pytest.fixture
def reset_tracer_provider():
    from opentelemetry.trace import _TRACER_PROVIDER_SET_ONCE

    with _TRACER_PROVIDER_SET_ONCE._lock:
        _TRACER_PROVIDER_SET_ONCE._done = False

    yield


@pytest.mark.unittest
@pytest.mark.usefixtures("reset_tracer_provider")
class TestStartTrace:
    def test_tracer_provider_after_start_trace(self) -> None:
        start_trace()
        tracer_provider = trace.get_tracer_provider()
        assert isinstance(tracer_provider, TracerProvider)
        attrs = tracer_provider.resource.attributes
        assert attrs[ResourceAttributesFieldName.SERVICE_NAME] == RESOURCE_ATTRIBUTES_SERVICE_NAME
        assert ResourceAttributesFieldName.COLLECTION not in attrs

    def test_tracer_provider_resource_attributes(self) -> None:
        collection = str(uuid.uuid4())
        res_attrs = {"attr1": "value1", "attr2": "value2"}
        start_trace(resource_attributes=res_attrs, collection=collection)
        tracer_provider: TracerProvider = trace.get_tracer_provider()
        attrs = tracer_provider.resource.attributes
        assert attrs[ResourceAttributesFieldName.COLLECTION] == collection
        assert attrs["attr1"] == "value1"
        assert attrs["attr2"] == "value2"

    def test_tracer_provider_resource_merge(self) -> None:
        existing_res = {"existing_attr": "existing_value"}
        trace.set_tracer_provider(TracerProvider(resource=Resource(existing_res)))
        start_trace()
        tracer_provider: TracerProvider = trace.get_tracer_provider()
        assert "existing_attr" in tracer_provider.resource.attributes
        assert ResourceAttributesFieldName.SERVICE_NAME in tracer_provider.resource.attributes

    def test_skip_tracing_local_setup(self, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
        spy = mocker.spy(promptflow.tracing._start_trace, "_is_devkit_installed")
        # configured environ to skip local setup
        with monkeypatch.context() as m:
            m.setenv(PF_TRACING_SKIP_LOCAL_SETUP_ENVIRON, "true")
            start_trace()
            assert spy.call_count == 0
        # no environ, should call local setup once
        start_trace()
        assert spy.call_count == 1
