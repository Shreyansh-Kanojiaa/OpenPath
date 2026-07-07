import { useEffect, useRef } from 'react'

const SPACING = 34
const BASE_SIZE = 1.8
const HOVER_SIZE = 3.8
const BASE_ALPHA = 0.05
const HOVER_ALPHA = 0.6
const RIPPLE_AMPLITUDE = 16
const FALLOFF_RADIUS = 230
const WAVE_FREQ = 0.05
const WAVE_SPEED = 0.005
const BG = '#05060b'
const BASE_COLOR = [255, 255, 255]
const ACCENT_COLOR = [134, 196, 187]
const EASE_IN = 0.09
const EASE_OUT = 0.12
const IDLE_EPSILON = 0.001

// Full-bleed dot grid that ripples outward from the cursor. Resting state is a
// flat static grid; hovering blends in a traveling radial sine wave whose
// amplitude/opacity/size/color all fade with distance from the pointer.
export default function DotGrid() {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    const parent = canvas.parentElement
    const ctx = canvas.getContext('2d')

    let width = 0
    let height = 0
    let rafId = null

    // Pointer is tracked on window (canvas has pointer-events: none, so it
    // can never receive its own events) and converted to canvas-local space
    // per-frame via getBoundingClientRect, which also tells us whether this
    // particular canvas is the one currently under the cursor.
    const pointer = { clientX: -9999, clientY: -9999 }
    const local = { x: -9999, y: -9999, hovering: false }
    const k = { value: 0 }
    let t = 0

    const drawDot = (x, y, size, color, alpha) => {
      ctx.fillStyle = `rgba(${color[0]},${color[1]},${color[2]},${alpha})`
      ctx.fillRect(x - size / 2, y - size / 2, size, size)
    }

    const drawStatic = () => {
      ctx.fillStyle = BG
      ctx.fillRect(0, 0, width, height)
      const cols = Math.ceil(width / SPACING) + 1
      const rows = Math.ceil(height / SPACING) + 1
      for (let i = 0; i < cols; i++) {
        const x = i * SPACING
        for (let j = 0; j < rows; j++) {
          drawDot(x, j * SPACING, BASE_SIZE, BASE_COLOR, BASE_ALPHA)
        }
      }
    }

    const drawFrame = () => {
      ctx.fillStyle = BG
      ctx.fillRect(0, 0, width, height)

      const cols = Math.ceil(width / SPACING) + 1
      const rows = Math.ceil(height / SPACING) + 1
      const kv = k.value

      for (let i = 0; i < cols; i++) {
        const x = i * SPACING
        for (let j = 0; j < rows; j++) {
          const y = j * SPACING

          const dx = x - local.x
          const dy = y - local.y
          const d = Math.sqrt(dx * dx + dy * dy)
          const falloff = Math.exp(-d / FALLOFF_RADIUS)
          const f = falloff * kv

          if (f < 0.003) {
            drawDot(x, y, BASE_SIZE, BASE_COLOR, BASE_ALPHA)
            continue
          }

          const wave = Math.sin(d * WAVE_FREQ - t * WAVE_SPEED)
          const offset = wave * RIPPLE_AMPLITUDE * f
          const nx = d > 0.001 ? dx / d : 0
          const ny = d > 0.001 ? dy / d : 0
          const px = x + nx * offset
          const py = y + ny * offset

          const size = BASE_SIZE + (HOVER_SIZE - BASE_SIZE) * f
          const alpha = BASE_ALPHA + (HOVER_ALPHA - BASE_ALPHA) * f
          const color = [
            BASE_COLOR[0] + (ACCENT_COLOR[0] - BASE_COLOR[0]) * f,
            BASE_COLOR[1] + (ACCENT_COLOR[1] - BASE_COLOR[1]) * f,
            BASE_COLOR[2] + (ACCENT_COLOR[2] - BASE_COLOR[2]) * f,
          ]
          drawDot(px, py, size, color, alpha)
        }
      }
    }

    const tick = () => {
      const rect = canvas.getBoundingClientRect()
      local.x = pointer.clientX - rect.left
      local.y = pointer.clientY - rect.top
      local.hovering =
        local.x >= 0 && local.x <= rect.width &&
        local.y >= 0 && local.y <= rect.height

      t = performance.now()
      k.value += local.hovering
        ? (1 - k.value) * EASE_IN
        : (0 - k.value) * EASE_OUT

      if (k.value < IDLE_EPSILON && !local.hovering) {
        k.value = 0
        drawStatic()
        rafId = null
        return
      }

      drawFrame()
      rafId = requestAnimationFrame(tick)
    }

    const ensureLoop = () => {
      if (rafId == null) rafId = requestAnimationFrame(tick)
    }

    const onPointerMove = (e) => {
      pointer.clientX = e.clientX
      pointer.clientY = e.clientY
      ensureLoop()
    }

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2)
      width = parent.clientWidth
      height = parent.clientHeight
      canvas.width = Math.round(width * dpr)
      canvas.height = Math.round(height * dpr)
      canvas.style.width = width + 'px'
      canvas.style.height = height + 'px'
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      if (k.value > 0 || local.hovering) drawFrame()
      else drawStatic()
    }

    resize()
    drawStatic()

    const resizeObserver = new ResizeObserver(resize)
    resizeObserver.observe(parent)
    window.addEventListener('pointermove', onPointerMove, { passive: true })

    return () => {
      resizeObserver.disconnect()
      window.removeEventListener('pointermove', onPointerMove)
      if (rafId != null) cancelAnimationFrame(rafId)
    }
  }, [])

  return <canvas ref={canvasRef} className="absolute inset-0 w-full h-full z-0 pointer-events-none" />
}
