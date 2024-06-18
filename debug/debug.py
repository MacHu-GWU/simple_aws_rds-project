# -*- coding: utf-8 -*-

from boto_session_manager import BotoSesManager
from simple_aws_rds.rds import RDSDBSnapshot
from rich import print as rprint

bsm = BotoSesManager(profile_name="bmt_app_dev_us_east_1")
snap_id = "sbx-blue-2023-06-19-22-25-00"
# snap = RDSDBSnapshot.from_id(rds_client=bsm.rds_client, db_snapshot_identifier=snap_id)
# res = bsm.rds_client.describe_db_snapshots(DBSnapshotIdentifier=)
# snapshot = RDSDBSnapshot.from_dict(res["DBSnapshots"][0])
# rprint(snap)

snap = RDSDBSnapshot(db_snapshot_identifier=snap_id).wait_for_available(rds_client=bsm.rds_client)
rprint(snap)
