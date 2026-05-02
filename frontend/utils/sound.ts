export async function playTimerExpiredAlert() {
  if (!import.meta.client) {
    return
  }

  const audioContext = new window.AudioContext()
  const beeps = [880, 880, 660]

  for (const [index, frequency] of beeps.entries()) {
    const start = audioContext.currentTime + index * 0.18
    const oscillator = audioContext.createOscillator()
    const gain = audioContext.createGain()
    oscillator.type = "sine"
    oscillator.frequency.value = frequency
    gain.gain.setValueAtTime(0.0001, start)
    gain.gain.exponentialRampToValueAtTime(0.12, start + 0.01)
    gain.gain.exponentialRampToValueAtTime(0.0001, start + 0.14)
    oscillator.connect(gain)
    gain.connect(audioContext.destination)
    oscillator.start(start)
    oscillator.stop(start + 0.15)
  }
}