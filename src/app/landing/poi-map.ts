import {
  AfterViewInit,
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  ElementRef,
  inject,
  input,
  OnChanges,
  viewChild,
} from '@angular/core';
import * as L from 'leaflet';

const DEFAULT_ZOOM = 15;

@Component({
  selector: 'app-poi-map',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<div #mapContainer class="map-container"></div>`,
  styles: `
    :host {
      display: block;
      height: 170px;
      border: 1px solid var(--color-divider);
    }
    .map-container {
      width: 100%;
      height: 100%;
    }
  `,
})
export class PoiMap implements AfterViewInit, OnChanges {
  readonly lat = input.required<number>();
  readonly lon = input.required<number>();

  private readonly mapEl = viewChild.required<ElementRef<HTMLElement>>('mapContainer');
  private readonly destroyRef = inject(DestroyRef);
  private map: L.Map | null = null;
  private marker: L.Marker | null = null;

  private readonly markerIcon = L.icon({
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    shadowSize: [41, 41],
  });

  ngAfterViewInit(): void {
    this.initMap();
    this.destroyRef.onDestroy(() => {
      this.map?.remove();
      this.map = null;
    });
  }

  ngOnChanges(): void {
    if (this.map) {
      this.updateMap();
    }
  }

  private initMap(): void {
    const el = this.mapEl().nativeElement;
    const coords: L.LatLngExpression = [this.lat(), this.lon()];

    this.map = L.map(el, {
      zoomControl: false,
      attributionControl: false,
      dragging: false,
      scrollWheelZoom: false,
      doubleClickZoom: false,
      touchZoom: false,
      boxZoom: false,
      keyboard: false,
    }).setView(coords, DEFAULT_ZOOM);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
    }).addTo(this.map);

    this.marker = L.marker(coords, { icon: this.markerIcon }).addTo(this.map);
  }

  private updateMap(): void {
    const coords: L.LatLngExpression = [this.lat(), this.lon()];
    this.map!.setView(coords, DEFAULT_ZOOM);
    this.marker?.setLatLng(coords);
  }
}
