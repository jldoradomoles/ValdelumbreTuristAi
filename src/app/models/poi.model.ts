export interface Franja {
  dias: number[];
  abre: string;
  cierra: string;
  temporada: string | null;
}

export interface Horario {
  always_open: boolean;
  franjas: Franja[];
}

export interface Precio {
  tipo: 'gratis' | 'fijo' | 'rango' | 'desconocido';
  valor: number | null;
  min: number | null;
  max: number | null;
}

export interface POIResponse {
  id: string;
  nombre: string;
  categoria: string;
  descripcion: string;
  lat: number;
  lon: number;
  accesible: boolean | null;
  horario: Horario;
  horario_desconocido: boolean;
  precio: Precio;
  etiquetas: string[];
}

export interface POIListResponse {
  total: number;
  pois: POIResponse[];
}

export interface PreguntarRequest {
  pregunta: string;
  idioma?: 'es' | 'en';
}

export interface PreguntarResponse {
  respuesta: string;
  pois: string[];
}
