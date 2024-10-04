import gsap from "gsap";
import { CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';

export function addRoomLabel(name, model, position, camera, controls, gui_folder=null) {
    const labelDiv = document.createElement('div');
    labelDiv.className = 'label';
    labelDiv.textContent = name;

    const label = new CSS2DObject(labelDiv);
    label.position.set(...position);
    label.center.set(0.5, 0.5);
    model.add(label);
    label.layers.set(0);

    if (gui_folder) {
        const labelPosition = { x: position.x, y: position.y, z: position.z };
        gui_folder.add(labelPosition, 'x', -5, 5).name(`${name} X`).onChange((value) => { label.position.x = value; });
        gui_folder.add(labelPosition, 'y', -5, 5).name(`${name} Y`).onChange((value) => { label.position.y = value; });
        gui_folder.add(labelPosition, 'z', -5, 5).name(`${name} Z`).onChange((value) => { label.position.z = value; });
    }

    labelDiv.addEventListener('click', () => {
        const targetPosition = { x: position.x, y: position.y + 3, z: position.z + 1 };

        gsap.to(camera.position, {
            x: targetPosition.x,
            y: targetPosition.y,
            z: targetPosition.z,
            duration: 1.5,
            ease: 'power2.inOut',
            onUpdate: () => {
                camera.updateProjectionMatrix();
            }
        });

        if (controls) {
            gsap.to(controls.target, {
                x: position.x,
                y: position.y,
                z: position.z,
                duration: 1.5,
                ease: 'power2.inOut',
                onUpdate: () => {
                    controls.update();
                }
            });
        }

        if(name === "Workspace"){
            const msg = {
                "people_count": {
                    "camera_id": "Q2PV-W8RK-DDVX",
                    "date_range": "7d"
                },
                "frame": {
                    "camera_id": "Q2PV-W8RK-DDVX",
                }
            };
            webSocketRequest(JSON.stringify(msg))
        }
        else if(name === "Kitchen"){
            const msg = {
                "people_count": {
                    "camera_id": "Q2PV-DZXG-F3GV",
                    "date_range": "7d"
                },
                "frame": {
                    "camera_id": "Q2PV-DZXG-F3GV",
                }
            };
            webSocketRequest(JSON.stringify(msg))
        }
        else{
            const msg = {
                "people_count": {
                    "camera_id": "Q2PV-EFHS-BMY5",
                    "date_range": "7d"
                },
                "frame": {
                    "camera_id": "Q2PV-EFHS-BMY5",
                }
            };
            webSocketRequest(JSON.stringify(msg))
        }
    });
}

export function webSocketRequest(msg){
    wait_for_socket_connection(window.webSocket, function() {
        window.webSocket.send(msg);
    });
}

function wait_for_socket_connection(socket, callback){
    setTimeout(
        function(){
            if (socket.readyState === 1) {
                if(callback !== undefined){
                    callback();
                }
                return;
            } 
            else {
                console.log("... waiting for web socket connection to come online");
                wait_for_socket_connection(socket,callback);
            }
        }, 5);
};