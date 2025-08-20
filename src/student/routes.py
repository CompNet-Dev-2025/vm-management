from flask import Flask, jsonify
from student_vm_management import StudentVMManager

app = Flask(__name__)

# Initialize VM manager with Proxmox credentials
vm_manager = StudentVMManager(
    proxmox_host="NEED FROM INFRASTRUCTURE TEAM",
    user="user",
    password="password",
    verify_ssl=False
)

def find_vm_by_id(vms, vmid):
    for v in vms:
        if v['vmid'] == vmid:
            return v
    return None

@app.route('/student/<student_id>/vms', methods=['GET'])
def get_student_vms(student_id):
    vms = vm_manager.get_student_vms(student_id)
    return jsonify(vms)

@app.route('/student/<student_id>/vm/<int:vmid>/start', methods=['POST'])
def start_vm(student_id, vmid):
    vms = vm_manager.get_student_vms(student_id)
    vm = find_vm_by_id(vms, vmid)
    if not vm:
        return jsonify({"error": "VM not found for student"}), 404

    vm_manager.start_vm(vm['node'], vmid)
    return jsonify({"message": f"VM {vmid} started."})

@app.route('/student/<student_id>/vm/<int:vmid>/stop', methods=['POST'])
def stop_vm(student_id, vmid):
    vms = vm_manager.get_student_vms(student_id)
    vm = find_vm_by_id(vms, vmid)
    if not vm:
        return jsonify({"error": "VM not found for student"}), 404

    vm_manager.stop_vm(vm['node'], vmid)
    return jsonify({"message": f"VM {vmid} stopped."})

@app.route('/student/<student_id>/vm/<int:vmid>/rdp', methods=['GET'])
def get_rdp_info(student_id, vmid):
    vms = vm_manager.get_student_vms(student_id)
    vm = find_vm_by_id(vms, vmid)
    if not vm:
        return jsonify({"error": "VM not found for student"}), 404

    rdp_info = vm_manager.get_vm_rdp_info(vm['node'], vmid)
    return jsonify(rdp_info)

@app.route('/student/<student_id>/vm/<int:vmid>/novnc', methods=['GET'])
def get_novnc_url(student_id, vmid):
    vms = vm_manager.get_student_vms(student_id)
    vm = find_vm_by_id(vms, vmid)
    if not vm:
        return jsonify({"error": "VM not found for student"}), 404

    novnc_url = vm_manager.get_vm_novnc_url(vm['node'], vmid)
    return jsonify({"novnc_url": novnc_url})


if __name__ == '__main__':
    app.run(debug=True)
