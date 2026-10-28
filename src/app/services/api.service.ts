import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  POIListResponse,
  POIResponse,
  PreguntarRequest,
  PreguntarResponse,
} from '../models/poi.model';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = '/api';

  listPois(): Observable<POIListResponse> {
    return this.http.get<POIListResponse>(`${this.baseUrl}/pois`);
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
}
