import * as THREE from 'three';
import GUI from 'lil-gui'; 

import { addRoomLabel } from './map_label.js';

import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';

const gui = new GUI();

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 6, 5);
camera.rotation.set(-1, 0, 0);

const renderer = new THREE.WebGLRenderer({ 
  canvas: document.querySelector('#canvas'),
  antialias: true
});
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const labelRenderer = new CSS2DRenderer();
labelRenderer.setSize(window.innerWidth, window.innerHeight);
labelRenderer.domElement.style.position = 'absolute';
labelRenderer.domElement.style.top = '0px';
document.body.appendChild(labelRenderer.domElement);

const cameraControls = new OrbitControls(camera, labelRenderer.domElement);
cameraControls.target.set( 0, 0, 0 );

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xbfe3dd);

const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(5, 10, 7.5).normalize();
scene.add(light);

const loader = new GLTFLoader();
loader.load(
  'assets/test.glb', 
  (gltf) => {
    const model = gltf.scene;
    scene.add(model);         

    model.position.set(0, 0, 0);
    model.scale.set(1, 1, 1);

    model.layers.enableAll();

    const labelFolder = gui.addFolder('Label Settings');
    addRoomLabel('Workspace', model, new THREE.Vector3(-0.6, 0.2, 3), camera, cameraControls);
    addRoomLabel('Kitchen', model, new THREE.Vector3(-2.5, 0, 1), camera, cameraControls);
    addRoomLabel('Lounge', model, new THREE.Vector3(-3.3, 0, -1.35), camera, cameraControls);
  }
);

window.onresize = function () {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  labelRenderer.setSize(window.innerWidth, window.innerHeight);
};

function animate() {
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
  labelRenderer.render(scene, camera);
}
animate();

const cameraFolder = gui.addFolder('Camera Settings');

const cameraPosition = { x: camera.position.x, y: camera.position.y, z: camera.position.z };
cameraFolder.add(cameraPosition, 'x', -10, 10).name('Camera X').onChange((value) => { camera.position.x = value; });
cameraFolder.add(cameraPosition, 'y', -10, 10).name('Camera Y').onChange((value) => { camera.position.y = value; });
cameraFolder.add(cameraPosition, 'z', 0, 20).name('Camera Z').onChange((value) => { camera.position.z = value; });

const cameraRotation = { x: camera.rotation.x, y: camera.rotation.y, z: camera.rotation.z };
cameraFolder.add(cameraRotation, 'x', -Math.PI, Math.PI).name('Rotation X').onChange((value) => { camera.rotation.x = value; });
cameraFolder.add(cameraRotation, 'y', -Math.PI, Math.PI).name('Rotation Y').onChange((value) => { camera.rotation.y = value; });
cameraFolder.add(cameraRotation, 'z', -Math.PI, Math.PI).name('Rotation Z').onChange((value) => { camera.rotation.z = value; });

const cameraFov = { fov: camera.fov };
cameraFolder.add(cameraFov, 'fov', 10, 100).name('Field of View').onChange((value) => {
  camera.fov = value;
  camera.updateProjectionMatrix();
});

cameraFolder.open();
