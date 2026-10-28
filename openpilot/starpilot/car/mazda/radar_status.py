"""Display-only radar ownership evidence; never grants driving authority."""
from opendbc.car.mazda.stock_ecu import StockEcuState
from openpilot.starpilot.ui.onroad_state import AlertSize, OnroadAlert

KEY = 'MazdaStockEcuStatus'
MAX_AGE_NS = 3_000_000_000
LABELS = {
  'starting': 'Preparing alpha long', 'parkToTakeOver': 'Waiting for the next stop',
  'stockCruiseOn': 'Factory cruise has control', 'ready': 'Alpha long ready',
  'restoring': 'Restoring factory radar', 'restored': 'Factory radar restored',
  'failed': 'Radar transition failed', 'notNeeded': 'Factory radar has control',
}


def fresh(record, now_ns):
  return bool(isinstance(record, dict) and type(record.get('state')) is str and record['state'] in set(StockEcuState) and
              type(record.get('radarOff')) is bool and type(record.get('alphaRequested')) is bool and
              type(record.get('fingerprint')) is str and type(record.get('monoTime')) is int and
              0 < record['monoTime'] <= now_ns and now_ns - record['monoTime'] <= MAX_AGE_NS)


def read(params):
  return params.get(KEY)


def status_text(record, restore_failed, now_ns, fingerprint=None):
  if restore_failed:
    return 'Radar restore failed; restart the vehicle'
  if not fresh(record, now_ns) or fingerprint is not None and record['fingerprint'] != fingerprint:
    return 'Waiting for current radar status'
  label = LABELS[record['state']]
  return label + ('; factory AEB off' if record['radarOff'] else '')


def notice(native, cp, record, restore_failed, now_ns):
  if native.size != AlertSize.NONE or cp is None or getattr(cp, 'brand', '') != 'mazda' or cp.notCar or cp.dashcamOnly:
    return native
  if restore_failed:
    return OnroadAlert(AlertSize.SMALL, 'Mazda radar restore failed', 'Restart the vehicle to restore factory cruise',
                       alert_type='mazdaRadarRestore/permanent')
  if not cp.openpilotLongitudinalControl or not fresh(record, now_ns) or record['fingerprint'] != cp.carFingerprint:
    return native
  if record['radarOff']:
    detail = 'Restoring factory radar' if record['state'] == 'restoring' else 'Mazda alpha longitudinal has radar control'
    return OnroadAlert(AlertSize.SMALL, 'Factory AEB off', detail, alert_type='mazdaRadarOwnership/permanent')
  if record['alphaRequested'] and record['state'] in ('starting', 'parkToTakeOver'):
    return OnroadAlert(AlertSize.SMALL, 'Alpha long requested', 'Takes over at the next stop',
                       alert_type='mazdaRadarTakeover/permanent')
  return native
