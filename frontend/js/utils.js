import gsap from "gsap";
import { CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import { webSocketRequest } from "./websocket";

export function addRoomLabel(name, model, position, camera, controls, gui_folder=null) {
    const labelDiv = document.createElement('div');
    labelDiv.className = 'label';
    labelDiv.textContent = name;
    labelDiv.style.pointerEvents = 'auto';
    
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
        let container = document.getElementById("side-panel-container");
        if (container.style.display === "none") {
            // Add a 1 sec delay to ensure that front-end has received the frames
            setTimeout(() => {
                container.style.display = "block";
            }, 1000);
        }

        // Reset toggle every time the user switches camera
        let camera_toggle = document.getElementById("camera-toggle");
        camera_toggle.checked = false;

        let selected_camera = document.getElementById("selected-camera");
        selected_camera.text = name;

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
                "hide_feed": false
            }
        };
        webSocketRequest(JSON.stringify(msg))
    });
}