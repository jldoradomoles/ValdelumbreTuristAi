import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  signal,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { forkJoin } from 'rxjs';
import { ApiService } from '../services/api.service';
import { Horario, POIResponse, Precio } from '../models/poi.model';
import { PoiMap } from './poi-map';

interface DisplayPOI {
  num: string;
  nombre: string;
  categoria: string;
  descripcion: string;
  horario: string;
  precio: string;
  coords: string;
  lat: number;
  lon: number;
  accesible: boolean | null;
}

@Component({
  selector: 'app-landing',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [FormsModule, PoiMap],
  templateUrl: './landing.html',
  styleUrl: './landing.scss',
})
export class Landing {
  private readonly api = inject(ApiService);

  readonly query = signal('');
  readonly loading = signal(false);
  readonly error = signal('');
  readonly lastQuery = signal('Un día de cultura y paseo en Valdelumbre');
  readonly results = signal<DisplayPOI[]>([]);
  readonly respuesta = signal('');

  readonly gridOpacity = computed(() => (this.loading() ? 0.35 : 1));
  readonly buttonLabel = computed(() =>
    this.loading() ? 'Buscando…' : 'Preguntar',
  );
  readonly resultsTitle = computed(() => {
    const count = this.results().length;
    return `${count} lugares en Valdelumbre`;
  });

  readonly suggestions = [
    '¿Qué monumentos puedo visitar hoy?',
    'Planes con niños en Valdelumbre',
    'Restaurantes accesibles',
    '¿Dónde puedo hacer senderismo?',
  ];

  constructor() {
    this.loadInitialPois();
  }

  onKeyDown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && (event.metaKey || event.ctrlKey)) {
      event.preventDefault();
      this.ask();
    }
  }

  pickSuggestion(text: string): void {
    this.query.set(text);
    this.ask(text);
  }

  ask(overrideQuery?: string): void {
    const question = (overrideQuery ?? this.query()).trim();
    if (!question || this.loading()) return;

    this.loading.set(true);
    this.error.set('');
    this.lastQuery.set(question);

    this.api.preguntar({ pregunta: question }).subscribe({
      next: (res) => {
        this.respuesta.set(res.respuesta);
        if (res.pois.length > 0) {
          this.fetchPoisByIds(res.pois);
        } else {
          this.results.set([]);
          this.loading.set(false);
        }
      },
      error: () => {
        this.error.set(
          'No pudimos obtener resultados. Reformula la pregunta o inténtalo de nuevo.',
        );
        this.loading.set(false);
      },
    });
  }

  private loadInitialPois(): void {
    this.api.listPois().subscribe({
      next: (res) => {
        this.results.set(
          res.pois.slice(0, 6).map((p, i) => this.toDisplay(p, i)),
        );
      },
    });
  }

  private fetchPoisByIds(ids: string[]): void {
    const requests = ids.map((id) => this.api.getPoi(id));
    forkJoin(requests).subscribe({
      next: (pois) => {
        this.results.set(pois.map((p, i) => this.toDisplay(p, i)));
        this.loading.set(false);
      },
      error: () => {
        this.error.set(
          'No pudimos obtener resultados. Reformula la pregunta o inténtalo de nuevo.',
        );
        this.loading.set(false);
      },
    });
  }

  private toDisplay(poi: POIResponse, index: number): DisplayPOI {
    return {
      num: String(index + 1).padStart(2, '0'),
      nombre: poi.nombre,
      categoria: poi.categoria,
      descripcion: poi.descripcion,
      horario: this.formatHorario(poi.horario, poi.horario_desconocido),
      precio: this.formatPrecio(poi.precio),
      coords: `${poi.lat.toFixed(4)}, ${poi.lon.toFixed(4)}`,
      lat: poi.lat,
      lon: poi.lon,
      accesible: poi.accesible,
    };
  }

  private formatHorario(horario: Horario, desconocido: boolean): string {
    if (desconocido) return 'Horario no disponible';
    if (horario.always_open) return 'Siempre abierto';
    if (horario.franjas.length === 0) return 'Consultar horario';

    const DAY_NAMES = ['L', 'M', 'X', 'J', 'V', 'S', 'D'];
    return horario.franjas
      .map((f) => {
        const dias = f.dias.map((d) => DAY_NAMES[d] ?? '?').join(', ');
        return `${dias} ${f.abre}–${f.cierra}`;
      })
      .join(' · ');
  }

  private formatPrecio(precio: Precio): string {
    switch (precio.tipo) {
      case 'gratis':
        return 'Gratis';
      case 'fijo':
        return `${precio.valor} €`;
      case 'rango':
        return `${precio.min}–${precio.max} €`;
      case 'desconocido':
        return 'Consultar precio';
    }
  }
}
