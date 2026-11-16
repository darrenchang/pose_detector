// Draws every registered card skeleton with ONE WebGL context.
//
// Browsers allow only ~16 live WebGL contexts per page and silently lose the
// oldest beyond that, so a canvas per card goes blank as soon as a large
// screen shows more cards than that. Instead this component lives inside a
// single <TresCanvas> laid over the card grid and, each frame it is asked to
// draw, clips the renderer to each card's on-screen rectangle (scissor +
// viewport) and renders that card's skeleton there: the classic three.js
// "multiple elements" technique.
import { defineComponent, onUnmounted, watch } from 'vue'
import type { PropType } from 'vue'
import { useLoop, useTresContext } from '@tresjs/core'
import {
  AmbientLight, Color, CylinderGeometry, DirectionalLight, Group, Mesh, MeshStandardMaterial,
  PerspectiveCamera, Scene, SphereGeometry,
} from 'three'
import type { CardViewRegistry, CardView } from '@/composables/cardViewRegistry'
import { buildSkeleton } from '@/composables/poseSkeleton'
import type { Joint, Bone } from '@/composables/poseSkeleton'

const BACKGROUND = new Color('#101826')
const CAMERA_DISTANCE = 4
const CAMERA_FOV = 40

export default defineComponent({
  name: 'PoseCardsRenderer',
  props: {
    registry: { type: Object as PropType<CardViewRegistry>, required: true },
  },
  setup(props) {
    const { renderer, sizes } = useTresContext()
    const { onBeforeRender } = useLoop()

    // Geometry and materials are shared by every card (unit shapes, scaled per
    // mesh), so a page of cards costs a handful of GPU buffers.
    const headGeometry = new SphereGeometry(1, 24, 24)
    const jointGeometry = new SphereGeometry(1, 16, 16)
    const handJointGeometry = new SphereGeometry(1, 10, 10)
    const boneGeometry = new CylinderGeometry(1, 1, 1, 12)
    const fingerGeometry = new CylinderGeometry(1, 1, 1, 8)
    const skinMaterial = new MeshStandardMaterial({ color: '#f4a259', roughness: 0.45, metalness: 0.1 })
    const boneMaterial = new MeshStandardMaterial({ color: '#3ddc97', roughness: 0.5, metalness: 0.1 })
    const fingerMaterial = new MeshStandardMaterial({ color: '#5bd1ff', roughness: 0.5, metalness: 0.1 })
    const handJointMaterial = new MeshStandardMaterial({ color: '#ffd166', roughness: 0.4, metalness: 0.1 })

    // One scene with the lights; the card being drawn is swapped in as `current`.
    const scene = new Scene()
    scene.add(new AmbientLight(0xffffff, 0.9))
    const key = new DirectionalLight(0xffffff, 1.6)
    key.position.set(2, 4, 5)
    scene.add(key)
    const fill = new DirectionalLight(0xffffff, 0.6)
    fill.position.set(-3, 1, 2)
    scene.add(fill)
    const camera = new PerspectiveCamera(CAMERA_FOV, 1, 0.1, 100)
    camera.position.set(0, 0, CAMERA_DISTANCE)
    camera.lookAt(0, 0, 0)
    let current: Group | null = null

    // Skeleton groups built once per card and kept while the card exists.
    const groups = new Map<string, Group>()

    function addJoints(group: Group, joints: Joint[], geometry: SphereGeometry, material: MeshStandardMaterial) {
      joints.forEach(j => {
        const m = new Mesh(geometry, material)
        m.position.set(j.position[0], j.position[1], j.position[2])
        m.scale.setScalar(j.radius)
        group.add(m)
      })
    }
    function addBones(group: Group, bones: Bone[], geometry: CylinderGeometry, material: MeshStandardMaterial) {
      bones.forEach(b => {
        const m = new Mesh(geometry, material)
        m.position.set(b.position[0], b.position[1], b.position[2])
        m.rotation.set(b.rotation[0], b.rotation[1], b.rotation[2])
        m.scale.set(b.scale[0], b.scale[1], b.scale[2])
        group.add(m)
      })
    }

    function groupFor(view: CardView): Group {
      let group = groups.get(view.id)
      if (group) return group
      const img = view.result.image
      const aspect = img.height > 0 ? img.width / img.height : 1
      const sk = buildSkeleton(view.result.pose_landmarks, view.result.hand_landmarks.left, view.result.hand_landmarks.right, aspect)
      group = new Group()
      if (sk.head) addJoints(group, [sk.head], headGeometry, skinMaterial)
      addJoints(group, sk.joints, jointGeometry, skinMaterial)
      addBones(group, sk.bones, boneGeometry, boneMaterial)
      addJoints(group, sk.handJoints, handJointGeometry, handJointMaterial)
      addBones(group, sk.handBones, fingerGeometry, fingerMaterial)
      groups.set(view.id, group)
      return group
    }

    function draw() {
      const gl = renderer.value
      if (!gl) return
      const canvasRect = gl.domElement.getBoundingClientRect()
      if (canvasRect.width === 0 || canvasRect.height === 0) return

      // Drop cached groups of cards that are gone.
      groups.forEach((_, id) => {
        if (!props.registry.views.has(id)) groups.delete(id)
      })

      // Clear the whole canvas to transparent, so regions no card covers any
      // more (removed, scrolled away) don't keep a stale skeleton.
      gl.setScissorTest(false)
      gl.setClearColor(0x000000, 0)
      gl.clear()
      gl.setScissorTest(true)
      gl.setClearColor(BACKGROUND, 1)

      props.registry.views.forEach(view => {
        const r = view.el.getBoundingClientRect()
        // Only cards that overlap the canvas (i.e. are on screen).
        if (r.bottom <= canvasRect.top || r.top >= canvasRect.bottom || r.right <= canvasRect.left || r.left >= canvasRect.right) return
        if (r.width < 1 || r.height < 1) return
        // Canvas-relative rectangle; GL's origin is the bottom-left corner.
        const x = r.left - canvasRect.left
        const y = canvasRect.bottom - r.bottom
        gl.setViewport(x, y, r.width, r.height)
        gl.setScissor(x, y, r.width, r.height)
        camera.aspect = r.width / r.height
        camera.updateProjectionMatrix()

        const group = groupFor(view)
        group.rotation.y = view.rotationY
        if (current !== group) {
          if (current) scene.remove(current)
          scene.add(group)
          current = group
        }
        gl.render(scene, camera)
      })
      gl.setScissorTest(false)
    }

    // Redraw whenever something changed: a registered/removed card, a drag, a
    // scroll or a resize (all of which call registry.invalidate()). A changed
    // drawing buffer (window resize, or a device-pixel-ratio change such as
    // moving the window to another display) starts empty, so that redraws too.
    let bufferW = 0
    let bufferH = 0
    onBeforeRender(() => {
      const el = renderer.value?.domElement
      const resized = !!el && (el.width !== bufferW || el.height !== bufferH)
      if (el && resized) {
        bufferW = el.width
        bufferH = el.height
      }
      if (props.registry.takeDirty() || resized) draw()
    })
    watch([sizes.width, sizes.height], () => props.registry.invalidate())

    onUnmounted(() => {
      ;[headGeometry, jointGeometry, handJointGeometry, boneGeometry, fingerGeometry].forEach(g => g.dispose())
      ;[skinMaterial, boneMaterial, fingerMaterial, handJointMaterial].forEach(m => m.dispose())
      groups.clear()
    })

    return () => null
  },
})
