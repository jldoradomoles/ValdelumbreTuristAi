import { Component } from '@angular/core';
import { Landing } from './landing/landing';

@Component({
  selector: 'app-root',
  imports: [Landing],
  templateUrl: './app.html',
})
export class App {}
