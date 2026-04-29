import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PanelUsuarios } from './panel-usuarios';

describe('PanelUsuarios', () => {
  let component: PanelUsuarios;
  let fixture: ComponentFixture<PanelUsuarios>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PanelUsuarios],
    }).compileComponents();

    fixture = TestBed.createComponent(PanelUsuarios);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
