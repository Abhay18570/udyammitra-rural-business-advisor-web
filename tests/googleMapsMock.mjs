import React from 'react'
export const APILoadingStatus = { LOADED: 'LOADED', FAILED: 'FAILED', AUTH_FAILURE: 'AUTH_FAILURE' }
export const useApiLoadingStatus = () => globalThis.mapTestStatus ?? 'LOADED'
export const useMap = () => null
export const APIProvider = ({ children }) => children
export const Map = ({ children }) => React.createElement('div', { 'data-google-map': true }, children)
export const AdvancedMarker = ({ children, position, title }) => React.createElement('div', { 'data-position': JSON.stringify(position), title }, children)
export const Pin = ({ background, glyph }) => React.createElement('span', { 'data-color': background }, glyph)
export const InfoWindow = ({ children }) => children
