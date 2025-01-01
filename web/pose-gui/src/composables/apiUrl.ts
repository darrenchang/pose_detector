export function getBaseApiUrl() {
  const protocol = window.location.protocol as string
  const hostname = window.location.hostname as string
  const apiUrl = `${protocol}//${hostname}:8000/api`
  return apiUrl
}
