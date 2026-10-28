import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  signal,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { forkJoin } from 'rxjs';
import { ApiService, ListPoisParams } from '../services/api.service';
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

  readonly selectedCategorias = signal<Set<string>>(new Set());
  readonly filtroAccesible = signal(false);
  readonly abiertoAhora = signal(false);
  readonly diaManual = signal<string | null>(null);
  readonly horaManual = signal<string | null>(null);
  private readonly isAiMode = signal(false);

  readonly categorias = [
    { key: 'espacio_publico', label: 'Espacio público' },
    { key: 'gastronomia', label: 'Gastronomía' },
    { key: 'monumento', label: 'Monumento' },
    { key: 'museo', label: 'Museo' },
    { key: 'naturaleza', label: 'Naturaleza' },
    { key: 'ruta', label: 'Ruta' },
    { key: 'servicio', label: 'Servicio' },
  ];

  readonly diasSemana = [
    { value: 'L', label: 'Lunes' },
    { value: 'M', label: 'Martes' },
    { value: 'X', label: 'Miércoles' },
    { value: 'J', label: 'Jueves' },
    { value: 'V', label: 'Viernes' },
    { value: 'S', label: 'Sábado' },
    { value: 'D', label: 'Domingo' },
  ];

  readonly filteredResults = computed(() => {
    const pois = this.results();
    const cats = this.selectedCategorias();
    if (cats.size === 0) return pois;
    return pois.filter((p) => cats.has(p.categoria));
  });

  readonly gridOpacity = computed(() => (this.loading() ? 0.35 : 1));
  readonly buttonLabel = computed(() =>
    this.loading() ? 'Buscando…' : 'Preguntar',
  );
  readonly resultsTitle = computed(() => {
    const count = this.filteredResults().length;
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
    this.logLlmProvider();
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

    this.clearFilters();
    this.isAiMode.set(true);
    this.loading.set(true);
    this.error.set('');
    this.lastQuery.set(question);

    this.api.preguntar({ pregunta: question }).subscribe({
      next: (res) => {
        console.log(`[Valdelumbre AI] Respuesta generada con LLM provider: ${res.llm_provider}`);
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

  toggleCategoria(key: string): void {
    this.switchToExploreMode();
    this.selectedCategorias.update((prev) => {
      const next = new Set(prev);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  }

  toggleAccesible(checked: boolean): void {
    this.switchToExploreMode();
    this.filtroAccesible.set(checked);
    this.loadPois();
  }

  toggleAbiertoAhora(checked: boolean): void {
    this.switchToExploreMode();
    this.abiertoAhora.set(checked);
    if (checked) {
      this.diaManual.set(null);
      this.horaManual.set(null);
    }
    this.loadPois();
  }

  onDiaManualChange(value: string): void {
    this.switchToExploreMode();
    this.diaManual.set(value || null);
    this.abiertoAhora.set(false);
    this.loadPois();
  }

  onHoraManualChange(value: string): void {
    this.switchToExploreMode();
    this.horaManual.set(value || null);
    this.abiertoAhora.set(false);
    this.loadPois();
  }

  clearManualTime(): void {
    this.diaManual.set(null);
    this.horaManual.set(null);
    this.loadPois();
  }

  clearFilters(): void {
    this.selectedCategorias.set(new Set());
    this.filtroAccesible.set(false);
    this.abiertoAhora.set(false);
    this.diaManual.set(null);
    this.horaManual.set(null);
  }

  private switchToExploreMode(): void {
    if (this.isAiMode()) {
      this.isAiMode.set(false);
      this.respuesta.set('');
      this.lastQuery.set('Explorando Valdelumbre');
      this.loadPois();
    }
  }

  private logLlmProvider(): void {
    this.api.getInfo().subscribe({
      next: (info) => {
        const label = info.llm_provider === 'claude' ? 'Claude (API)' : 'Fallback (keyword matching)';
        console.log(`[Valdelumbre AI] LLM Provider activo: ${label} (${info.llm_provider})`);
      },
    });
  }

  private loadInitialPois(): void {
    this.loadPois();
  }

  private loadPois(): void {
    const params: ListPoisParams = {};
    if (this.filtroAccesible()) {
      params.accesible = true;
    }
    const abiertoEn = this.buildAbiertoEn();
    if (abiertoEn) {
      params.abierto_en = abiertoEn;
    }
    this.api.listPois(params).subscribe({
      next: (res) => {
        this.results.set(res.pois.map((p, i) => this.toDisplay(p, i)));
      },
    });
  }

  private buildAbiertoEn(): string | undefined {
    if (this.abiertoAhora()) {
      const now = new Date();
      const dayInitials: Record<number, string> = { 1: 'L', 2: 'M', 3: 'X', 4: 'J', 5: 'V', 6: 'S', 7: 'D' };
      const jsDay = now.getDay();
      const day = dayInitials[jsDay === 0 ? 7 : jsDay];
      const hh = String(now.getHours()).padStart(2, '0');
      const mm = String(now.getMinutes()).padStart(2, '0');
      return `${day}-${hh}:${mm}`;
    }
    const dia = this.diaManual();
    const hora = this.horaManual();
    if (dia && hora) {
      return `${dia}-${hora}`;
    }
    return undefined;
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

    const DAY_NAMES: Record<number, string> = { 1: 'L', 2: 'M', 3: 'X', 4: 'J', 5: 'V', 6: 'S', 7: 'D' };
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
