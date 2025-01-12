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
        var container = document.getElementById("side-panel-container");
        if (container.style.display === "none") {
            // Add a 1 sec delay to ensure that front-end has received the frames
            setTimeout(() => {
                container.style.display = "block";
            }, 1000);
        }

        const targetPosition = { x: position.x, y: position.y + 4.5, z: position.z + 1.5 };

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

        const msg = {
            "people_count": {
                "camera_name": name,
                "date_range": "7d"
            },
            "frame": {
                "camera_name": name,
            }
        };
        webSocketRequest(JSON.stringify(msg))
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