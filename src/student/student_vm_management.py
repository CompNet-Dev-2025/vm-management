from proxmoxer import ProxmoxAPI 
import os 
import logging 

logger = logging.getLogger(__name__)

 # VM.Audit permission must be enabled in Proxmox to get VM information 

class StudentVMManager:
    def __init__(self):
        self.proxmox_host = os.environ.get("PROXMOX_HOST")
        self.user = os.environ.get("PROXMOX_USER")
        self.password = os.environ.get("PROXMOX_PASS")
        verify = os.environ.get("PROXMOX_VERIFY_SSL", "false").lower() in ("1", "true", "yes")
        if not self.proxmox_host or not self.user or not self.password:
            raise RuntimeError("Missing Proxmox environment variables. Check .env")
        
        host = self.proxmox_host.replace("https://", "").replace("http://", "")
        self.proxmox = ProxmoxAPI(host, user=self.user, password=self.password, verify_ssl=verify)

    def get_student_vms(self, student_id:str):
        vms = []
        nodes = self.proxmox.nodes.get()
        for node in nodes:
            try:
                vmlist = self.proxmox.nodes(node['node']).qemu.get() # Requires name of each proxmox node
            except Exception as e: 
                logger.warning(f"Failed to list VMs on node {node['node']}: {e}")
                continue

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

    def reboot_vm(self, node, vmid):
        try:
            return self.proxmox.nodes(node).qemu(vmid).status.reboot.post()
        except Exception as e:
            logger.error(f"Failed to reboot VM {vmid} on node {node}: {e}")
            raise


    # option 1: RDP, returns IP address      
    def get_vm_rdp_info(self, node, vmid):
        return {"RDP not implemented yet"} 
    
    # option 2: noVNC, browser based remote console URL 
    def get_auth_ticket(self):
        auth = self.proxmox.access.ticket.post(
            username=self.user,
            password=self.password
        )
        return auth.get('ticket'), auth.get('CSRFPreventionToken')

    def get_vm_novnc_url(self, node, vmid, ticket):
        url = (
            f"https://{self.proxmox_host}:8006/?console=kvm&novnc=1"
            f"&node={node}&vmid={vmid}"
            f"&username={self.user}&ticket={ticket}"
        )
        return url