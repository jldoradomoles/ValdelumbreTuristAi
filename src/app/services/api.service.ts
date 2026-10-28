import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  AppInfo,
  POIListResponse,
  POIResponse,
  PreguntarRequest,
  PreguntarResponse,
} from '../models/poi.model';

export interface ListPoisParams {
  accesible?: boolean;
  abierto_en?: string;
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = '/api';

  listPois(filters?: ListPoisParams): Observable<POIListResponse> {
    let params = new HttpParams();
    if (filters?.accesible != null) {
      params = params.set('accesible', String(filters.accesible));
    }
    if (filters?.abierto_en) {
      params = params.set('abierto_en', filters.abierto_en);
    }
    return this.http.get<POIListResponse>(`${this.baseUrl}/pois`, { params });
  }

  getPoi(id: string): Observable<POIResponse> {
    return this.http.get<POIResponse>(`${this.baseUrl}/pois/${id}`);
  }

  preguntar(request: PreguntarRequest): Observable<PreguntarResponse> {
    return this.http.post<PreguntarResponse>(
      `${this.baseUrl}/preguntar`,
      request,
    );
  }

  getInfo(): Observable<AppInfo> {
    return this.http.get<AppInfo>(`${this.baseUrl}/info`);
  }
}
