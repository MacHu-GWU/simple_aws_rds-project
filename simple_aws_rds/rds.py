# -*- coding: utf-8 -*-

"""
Abstract dataclass for RDS DB instance, cluster.
"""

import typing as T
import enum
import dataclasses
from datetime import datetime
from func_args import resolve_kwargs, NOTHING
from iterproxy import IterProxy

if T.TYPE_CHECKING:  # pragma: no cover
    from boto_session_manager import BotoSesManager


class RDSDBInstanceStatusEnum(str, enum.Enum):
    available = "available"
    stopped = "stopped"


@dataclasses.dataclass
class RDSDBInstance:
    """
    Represent an RDS DB instance.
    """

    id: str = dataclasses.field()
    status: str = dataclasses.field()
    instance_class: T.Optional[str] = dataclasses.field(default=None)
    instance_create_time: T.Optional[datetime] = dataclasses.field(default=None)
    engine: T.Optional[str] = dataclasses.field(default=None)
    engine_version: T.Optional[str] = dataclasses.field(default=None)
    endpoint: T.Optional[str] = dataclasses.field(default=None)
    port: T.Optional[int] = dataclasses.field(default=None)
    hosted_zone_id: T.Optional[str] = dataclasses.field(default=None)
    vpc_id: T.Optional[str] = dataclasses.field(default=None)
    subnet_ids: T.List[str] = dataclasses.field(default_factory=list)
    security_groups: T.List[T.Dict[str, str]] = dataclasses.field(default_factory=list)
    availability_zone: T.Optional[str] = dataclasses.field(default=None)
    publicly_accessible: T.Optional[bool] = dataclasses.field(default=None)
    tags: T.Dict[str, str] = dataclasses.field(default_factory=dict)
    data: T.Dict[str, T.Any] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_dict(cls, dct: dict):
        """
        Create an RDS DB instance object from the ``describe_db_instances`` API response.

        Ref:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/docdb/client/describe_db_instances.html
        """
        return cls(
            id=dct["DBInstanceIdentifier"],
            status=dct["DBInstanceStatus"],
            instance_class=dct.get("DBInstanceClass"),
            engine=dct.get("Engine"),
            engine_version=dct.get("EngineVersion"),
            endpoint=dct.get("Endpoint", {}).get("Address"),
            port=dct.get("Endpoint", {}).get("Port"),
            hosted_zone_id=dct.get("Endpoint", {}).get("HostedZoneId"),
            instance_create_time=dct.get("InstanceCreateTime"),
            vpc_id=dct.get("DBSubnetGroup", {}).get("VpcId"),
            subnet_ids=[
                kv["SubnetIdentifier"]
                for kv in dct.get("DBSubnetGroup", {}).get("Subnets", [])
            ],
            security_groups=dct["DBInstanceStatus"],
            availability_zone=dct["AvailabilityZone"],
            publicly_accessible=dct.get("PubliclyAccessible"),
            tags={d["Key"]: d["Value"] for d in dct.get("TagList", [])},
            data=dct,
        )

    def is_available(self) -> bool:
        """ """
        return self.status == RDSDBInstanceStatusEnum.available.value

    def is_stopped(self) -> bool:
        """ """
        return self.status == RDSDBInstanceStatusEnum.stopped.value

    def is_ready_to_start(self) -> bool:
        """ """
        return self.is_stopped()

    def is_ready_to_stop(self) -> bool:
        """ """
        return self.is_available()

    def start_db_instance(self, bsm: "BotoSesManager") -> dict:
        """ """
        return bsm.rds_client.start_db_instance(DBInstanceIdentifier=self.id)

    def stop_db_instance(self, bsm: "BotoSesManager") -> dict:
        """ """
        return bsm.rds_client.stop_db_instance(DBInstanceIdentifier=self.id)

    # --------------------------------------------------------------------------
    # more constructor methods
    # --------------------------------------------------------------------------
    @classmethod
    def _yield_dict_from_describe_db_instances_response(
        cls,
        res: dict,
    ) -> T.Iterable["RDSDBInstance"]:
        db_instances = res.get("DBInstances", [])
        if len(db_instances):
            for db_instance_dict in db_instances:
                yield cls.from_dict(db_instance_dict)

    @classmethod
    def query(
        cls,
        bsm: "BotoSesManager",
        db_instance_identifier: str = NOTHING,
        filters: T.List[dict] = NOTHING,
    ) -> "RDSDBInstanceIterProxy":
        def run():
            paginator = bsm.rds_client.get_paginator("describe_db_instances")
            kwargs = resolve_kwargs(
                DBInstanceIdentifier=db_instance_identifier,
                Filters=filters,
                PaginationConfig={
                    "MaxItems": 9999,
                    "PageSize": 100,
                },
            )
            if db_instance_identifier is not NOTHING:
                del kwargs["PaginationConfig"]
            response_iterator = paginator.paginate(**kwargs)
            for response in response_iterator:
                yield from cls._yield_dict_from_describe_db_instances_response(response)

        return RDSDBInstanceIterProxy(run())

    @classmethod
    def from_id(
        cls, bsm: "BotoSesManager", db_identifier: str
    ) -> T.Optional["RDSDBInstance"]:
        return cls.query(
            bsm,
            db_instance_identifier=db_identifier,
        ).one_or_none()

    @classmethod
    def from_tag_key_value(
        cls,
        bsm: "BotoSesManager",
        key: str,
        value: str,
    ) -> "RDSDBInstanceIterProxy":
        def run():
            for db_inst in cls.query(bsm):
                if db_inst.tags.get(key, "THIS_IS_IMPOSSIBLE_TO_MATCH") == value:
                    yield db_inst

        return RDSDBInstanceIterProxy(run())


class RDSDBInstanceIterProxy(IterProxy[RDSDBInstance]):
    """
    IterProxy for RDSDBInstance.
    """

    pass


# TODO: implement RDS DB Cluster
# @dataclasses.dataclass
# class RDSDBCluster:
#     pass
#
#
# class RDSDBClusterIterProxy(IterProxy[RDSDBCluster]):
#     """
#     IterProxy for RDSDBCluster.
#     """
#
#     pass
