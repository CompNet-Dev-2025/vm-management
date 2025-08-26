import time
import logging
from flask import Flask, jsonify, g, request
from dotenv import load_dotenv
from student_vm_management import StudentVMManager
from student_auth import require_auth, enforce_student_identity
from logging_config import logging_service

# Setup
logging_service()
logger = logging.getLogger(__name__)
load_dotenv()
app = Flask(__name__)
vm_manager = StudentVMManager()
last_reboots = {}  # {(student_id, vmid): timestamp}

# Helpers
def find_vm_by_id(vms, vmid):
    for v in vms:
        if v["vmid"] == vmid:
            return v
    return None

def validate_ids(student_id, vmid=None):
    if not student_id.isdigit():
        logger.warning(f"Invalid student_id: {student_id}")
        return jsonify({"error": "student_id must be numeric"}), 400
    if vmid is not None:
        if not isinstance(vmid, int) or vmid <= 0:
            logger.warning(f"Invalid vmid: {vmid} for student {student_id}")
            return jsonify({"error": "vmid must be a positive integer"}), 400
    return None

# Routes
@app.route('/student/<student_id>/vms', methods=['GET'])
@require_auth
@enforce_student_identity
def get_student_vms(student_id):
    err = validate_ids(student_id)
    if err:
        return err
    vms = vm_manager.get_student_vms(student_id)
    return jsonify(vms)

@app.route('/student/<student_id>/vm/<int:vmid>/reboot', methods=['POST'])
@require_auth
@enforce_student_identity
def reboot_vm(student_id, vmid):
    err = validate_ids(student_id, vmid)
    if err:
        return err

    vms = vm_manager.get_student_vms(student_id)
    vm = find_vm_by_id(vms, vmid)
    if not vm:
        return jsonify({"error": "VM not found"}), 404

    key = (student_id, vmid)
    now = time.time()
    if key in last_reboots and now - last_reboots[key] < 120:
        remaining = 120 - int(now - last_reboots[key])
        return jsonify({"error": f"Reboot cooldown. Try again in {remaining} seconds."}), 429

    try:
        vm_manager.reboot_vm(vm["node"], vmid)
        last_reboots[key] = now
        return jsonify({"message": f"Rebooting VM {vmid}"})
    except Exception as e:
        logger.error(f"Failed reboot VM {vmid}: {e}")
        return jsonify({"error": "Failed to reboot VM"}), 500

@app.route('/student/<student_id>/vm/<int:vmid>/rdp', methods=['GET'])
@require_auth
@enforce_student_identity
def get_rdp_info(student_id, vmid):
    err = validate_ids(student_id, vmid)
    if err:
        return err
    vms = vm_manager.get_student_vms(student_id)
    vm = find_vm_by_id(vms, vmid)
    if not vm:
        return jsonify({"error": "VM not found"}), 404
    return jsonify(vm_manager.get_vm_rdp_info(vm["node"], vmid))

@app.route('/student/<student_id>/vm/<int:vmid>/novnc', methods=['GET'])
@require_auth
@enforce_student_identity
def get_novnc_url(student_id, vmid):
    err = validate_ids(student_id, vmid)
    if err:
        return err
    vms = vm_manager.get_student_vms(student_id)
    vm = find_vm_by_id(vms, vmid)
    if not vm:
        return jsonify({"error": "VM not found"}), 404
    ticket, _ = vm_manager.get_auth_ticket()
    return jsonify({"novnc_url": vm_manager.get_vm_novnc_url(vm["node"], vmid, ticket)})


if __name__ == '__main__':
    app.run(debug=True)
