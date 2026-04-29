import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Backoffice } from './backoffice';

describe('Backoffice', () => {
  let component: Backoffice;
  let fixture: ComponentFixture<Backoffice>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Backoffice],
    }).compileComponents();

    fixture = TestBed.createComponent(Backoffice);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
