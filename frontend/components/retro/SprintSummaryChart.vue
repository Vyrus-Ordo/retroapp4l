<template>
  <div class="panel p-6 flex flex-col gap-4">
    <h3 class="text-xs text-zinc-500 uppercase tracking-[0.2em]">Delivery Rate History</h3>

    <div v-if="current.delivery_rate === null" class="text-sm text-zinc-600">
      Sem dados para exibir.
    </div>

    <template v-else-if="!showChart">
      <div class="flex items-center gap-3">
        <div class="flex-1 h-2 rounded-full bg-white/10 overflow-hidden">
          <div
            class="h-full rounded-full bg-[#00f2ff] transition-all"
            :style="{ width: `${current.delivery_rate}%` }"
          />
        </div>
        <span class="text-sm text-[#00f2ff] font-light min-w-[3rem] text-right">
          {{ current.delivery_rate }}%
        </span>
      </div>
    </template>

    <template v-else>
      <svg viewBox="0 0 600 200" class="w-full" aria-hidden="true">
        <g v-for="pct in Y_REFS" :key="pct">
          <line
            :x1="PAD.left"
            :y1="yPos(pct)"
            :x2="600 - PAD.right"
            :y2="yPos(pct)"
            stroke="rgba(255,255,255,0.08)"
            stroke-width="1"
          />
          <text :x="PAD.left - 4" :y="yPos(pct) + 4" text-anchor="end" font-size="9" fill="#52525b">
            {{ pct }}%
          </text>
        </g>

        <polyline :points="polylinePoints" stroke="#00f2ff" stroke-width="1.5" fill="none" />

        <g v-for="(point, i) in allPoints.slice(0, -1)" :key="`h-${i}`">
          <title>{{ point.label }}: {{ point.rate }}%</title>
          <circle :cx="xPos(i)" :cy="yPos(point.rate)" r="4" fill="#00f2ff" />
        </g>

        <polygon
          :points="diamondPoints(xPos(allPoints.length - 1), yPos(allPoints[allPoints.length - 1].rate))"
          fill="#00f2ff"
          stroke="white"
          stroke-width="1"
        />

        <text
          v-for="(point, i) in allPoints"
          :key="`l-${i}`"
          :x="xPos(i)"
          :y="200 - PAD.bottom + 14"
          text-anchor="middle"
          font-size="9"
          fill="#52525b"
        >
          {{ truncate(point.label) }}
        </text>
      </svg>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { SprintSummary, SprintSummaryHistory } from '~/utils/types'

const props = defineProps<{
  history: SprintSummaryHistory[]
  current: SprintSummary
}>()

const PAD = { top: 20, right: 20, bottom: 40, left: 40 }
const W = 600
const H = 200
const Y_REFS = [25, 50, 75, 100]

const showChart = computed(() => props.history.length >= 2)

interface ChartPoint {
  label: string
  rate: number
}

const allPoints = computed((): ChartPoint[] => {
  const historical = props.history.map((h, i) => ({
    label: h.sprint_name ?? `Sprint ${i + 1}`,
    rate: h.delivery_rate ?? 0,
  }))
  return [...historical, { label: 'Current', rate: props.current.delivery_rate ?? 0 }]
})

function xPos(index: number): number {
  const n = allPoints.value.length
  const innerW = W - PAD.left - PAD.right
  return n === 1 ? PAD.left + innerW / 2 : PAD.left + (index / (n - 1)) * innerW
}

function yPos(pct: number): number {
  return PAD.top + (1 - pct / 100) * (H - PAD.top - PAD.bottom)
}

const polylinePoints = computed(() =>
  allPoints.value.map((p, i) => `${xPos(i)},${yPos(p.rate)}`).join(' '),
)

function diamondPoints(cx: number, cy: number): string {
  const r = 6
  return `${cx},${cy - r} ${cx + r},${cy} ${cx},${cy + r} ${cx - r},${cy}`
}

function truncate(str: string, max = 8): string {
  return str.length > max ? `${str.slice(0, max)}…` : str
}
</script>
