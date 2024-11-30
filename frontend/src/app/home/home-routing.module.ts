import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomePage } from './home.page';
import { ResultPage } from '../result/result.page';

const routes: Routes = [
  {
    path: '',
    component: HomePage,
  },
  {
    path: '',
    component: ResultPage,
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class HomePageRoutingModule {}
