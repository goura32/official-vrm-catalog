import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { VRMLoaderPlugin, VRMUtils } from '@pixiv/three-vrm';

window.previewStatus = { state: 'loading' };

try {
  const params = new URLSearchParams(window.location.search);
  const view = params.get('view');
  if (!['tpose', 'face'].includes(view)) throw new Error('Invalid view');
  const yawDegrees = Number(params.get('yaw') ?? 0);
  if (!Number.isFinite(yawDegrees) || Math.abs(yawDegrees) > 360) throw new Error('Invalid yaw angle');
  const faceYOffset = Number(params.get('faceY') ?? 0);
  if (!Number.isFinite(faceYOffset) || Math.abs(faceYOffset) > 1) throw new Error('Invalid face Y offset');
  const faceHeight = Number(params.get('faceHeight') ?? 0.34);
  if (!Number.isFinite(faceHeight) || faceHeight < 0.1 || faceHeight > 1) throw new Error('Invalid face height fraction');
  const width = view === 'tpose' ? 768 : 512;
  const height = view === 'tpose' ? 1024 : 512;
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setPixelRatio(1);
  renderer.setSize(width, height);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.setClearColor(0xe6e9ed, 1);
  document.body.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xe6e9ed);
  const ambient = new THREE.HemisphereLight(0xffffff, 0x9ba7b5, 2.0);
  const key = new THREE.DirectionalLight(0xffffff, 2.3);
  key.position.set(2, 4, 5);
  scene.add(ambient, key);
  const loader = new GLTFLoader();
  loader.register((parser) => new VRMLoaderPlugin(parser));
  const gltf = await loader.loadAsync('/model.vrm');
  const vrm = gltf.userData.vrm;
  if (!vrm?.humanoid) throw new Error('VRM humanoid could not be loaded');
  VRMUtils.rotateVRM0(vrm);
  vrm.scene.rotation.y += THREE.MathUtils.degToRad(yawDegrees);
  vrm.humanoid.resetNormalizedPose();
  vrm.humanoid.update();
  vrm.update(0);
  scene.add(vrm.scene);
  vrm.scene.updateMatrixWorld(true);

  const bounds = new THREE.Box3().setFromObject(vrm.scene);
  const boxSize = bounds.getSize(new THREE.Vector3());
  const center = bounds.getCenter(new THREE.Vector3());
  if (bounds.isEmpty() || boxSize.y <= 0.05) throw new Error('Empty model bounds');
  let target = center.clone();
  // T-posed arms are often wider than the height-based camera framing.
  // Ensure BOTH dimensions fit in the 3:4 orthographic viewport.
  let visibleHeight = Math.max(boxSize.y * 1.18, (boxSize.x / (width / height)) * 1.18);
  if (view === 'face') {
    const head = vrm.humanoid.getNormalizedBoneNode('head');
    if (!head) throw new Error('Missing head bone; manual face capture required');
    const headPos = head.getWorldPosition(new THREE.Vector3());
    target = new THREE.Vector3(headPos.x, headPos.y - boxSize.y * 0.035 + boxSize.y * faceYOffset, headPos.z);
    visibleHeight = Math.max(boxSize.y * faceHeight, 0.2);
  }

  const aspect = width / height;
  const halfH = visibleHeight / 2;
  const camera = new THREE.OrthographicCamera(
    -halfH * aspect, halfH * aspect, halfH, -halfH, 0.01, 1000,
  );
  // rotateVRM0 normalizes the front direction: VRM 1.0 and 0.x face +Z.
  const distance = Math.max(boxSize.x, boxSize.y, boxSize.z, 1) * 2.5;
  camera.position.set(target.x, target.y, Math.max(bounds.max.z, target.z) + distance);
  camera.lookAt(target);
  camera.updateProjectionMatrix();
  renderer.render(scene, camera);
  // Signal readiness only after a complete render.
  window.previewStatus = { state: 'ready', view, width, height };
} catch (error) {
  window.previewStatus = { state: 'error', message: String(error?.stack || error) };
}
