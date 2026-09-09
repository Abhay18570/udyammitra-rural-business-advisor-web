/** Visual geometry only: radius and marker positions come from the saved API evidence. */
export function createSearchArea(map: google.maps.Map, latitude: number, longitude: number, radiusMeters: number, positions: google.maps.LatLngLiteral[]) {
  const circle = new google.maps.Circle({ map, center: { lat: latitude, lng: longitude }, radius: radiusMeters,
    strokeColor: '#2563eb', strokeOpacity: 0.8, strokeWeight: 2, fillColor: '#2563eb', fillOpacity: 0.07, clickable: false })
  const bounds = circle.getBounds()!
  for (const position of positions) bounds.extend(position)
  return { circle, bounds }
}
