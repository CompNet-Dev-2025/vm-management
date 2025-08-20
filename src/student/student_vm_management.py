from proxmoxer import ProxmoxAPI

 # VM.Audit permission must be enabled in Proxmox to get VM information 

class StudentVMManager:
    def __init__(self, proxmox_host, user, password, verify_ssl=False):
        self.proxmox = ProxmoxAPI(proxmox_host, user=user, password=password, verify_ssl=verify_ssl)
        
    def get_student_vms(self, student_id):
        vms = []
        nodes = self.proxmox.nodes.get()
        for node in nodes:
            vmlist = self.proxmox.nodes(node['node']).qemu.get() # Requires name of each proxmox node
            for vm in vmlist:
                if f"student-{student_id}" in vm.get('name', ''):
                    vms.append({
                        'vmid': vm['vmid'],  
                        'status': self.get_vm_status(node['node'], vm['vmid']),
                        'node': node['node'],
                        'name': vm['name'], # Optional, may not be set 
                    })
        return vms
    
    def get_vm_status(self, node, vmid):
        status = self.proxmox.nodes(node).qemu(vmid).status.current.get()
        return status.get('status')

    def start_vm(self, node, vmid):
        return self.proxmox.nodes(node).qemu(vmid).status.start.post()

    def stop_vm(self, node, vmid):
        return self.proxmox.nodes(node).qemu(vmid).status.stop.post()

    # option 1: RDP, returns IP address      
    def get_vm_rdp_info(self, node, vmid):
        return True 
    
    # option 2: noVNC, browser based remote console URL 
    def get_vm_novnc_url(self, node, vmid, proxmox_host, proxmox_user, ticket):
        url = (
            f"https://{proxmox_host}:8006/?console=kvm&novnc=1"
            f"&node={node}&vmid={vmid}"
            f"&username={proxmox_user}&ticket={ticket}"
        )
        return url