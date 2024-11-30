import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.scss'],
})
export class HomePage {

  constructor(private router: Router) {}

  // Routing to go to result page
  navigateToResult() {
    this.router.navigate(['/result'])
  }

  // Function: returning value of ion-range including € symbol
  pinFormatter(value: number) {
    return `${value}€`;
  }
  
}
