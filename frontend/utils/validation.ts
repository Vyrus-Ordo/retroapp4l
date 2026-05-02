export function isEmail(value: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
}

export function required(value: string | null | undefined) {
  return Boolean(value && value.trim())
}

export function minLength(value: string, length: number) {
  return value.trim().length >= length
}