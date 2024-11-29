import { Component } from '@angular/core';

@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.scss'],
})
export class HomePage {

  constructor() {}

  // function: returning value of ion-range including € symbol
  pinFormatter(value: number) {
    return `${value} €`;
  }
  

}
