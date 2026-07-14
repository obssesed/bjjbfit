import { Component, OnInit, ChangeDetectorRef, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { AuthService, Plan } from '../../services/auth.service';
import { ClasesService, Actividad, Producto } from '../../services/clases.service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './landing.component.html',
  styleUrls: ['../home/home.component.css', './landing.component.css']
})
export class LandingComponent implements OnInit {
  activeTab: string = 'nosotros';
  videoMuted: boolean = true;
  actividades: Actividad[] = [];
  cargandoActividades: boolean = true;
  productos: Producto[] = [];
  cargandoProductos: boolean = true;
  planes: Plan[] = [];
  cargandoPlanes: boolean = true;

  @ViewChild('videoAcademia') videoRef!: ElementRef<HTMLVideoElement>;

  constructor(
    private authService: AuthService,
    private clasesService: ClasesService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    // Redirigir si ya está logueado
    if (this.authService.isLoggedIn()) {
      this.router.navigate(['/home']);
      return;
    }

    this.cargarActividades();
    this.cargarProductos();
    this.cargarPlanes();
  }

  setTab(tab: string) {
    this.activeTab = tab;
    setTimeout(() => {
      const el = document.querySelector('.home-main');
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 50);
  }

  videoFullscreen(event: Event) {
    const video = (event.target as HTMLElement).closest('.about-video')?.querySelector('video');
    if (video) {
      if (video.requestFullscreen) {
        video.requestFullscreen();
      } else if ((video as any).webkitRequestFullscreen) {
        (video as any).webkitRequestFullscreen();
      }
    }
  }

  toggleMute() {
    this.videoMuted = !this.videoMuted;
    if (this.videoRef?.nativeElement) {
      this.videoRef.nativeElement.muted = this.videoMuted;
    }
  }

  cargarActividades() {
    this.cargandoActividades = true;
    this.clasesService.getActividades().subscribe({
      next: (data) => {
        this.actividades = data;
        this.cargandoActividades = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error al cargar actividades:', err);
        this.cargandoActividades = false;
        this.cdr.detectChanges();
      }
    });
  }

  cargarProductos() {
    this.cargandoProductos = true;
    this.clasesService.getProductos().subscribe({
      next: (data) => {
        this.productos = data;
        this.cargandoProductos = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error al cargar productos:', err);
        this.cargandoProductos = false;
        this.cdr.detectChanges();
      }
    });
  }

  cargarPlanes() {
    this.cargandoPlanes = true;
    this.authService.getPlanes().subscribe({
      next: (res: Plan[]) => {
        // Mostrar solo planes activos y ocultar explícitamente el plan "Plan adulto fundador"
        this.planes = res.filter(p => 
          p.activo && p.nombre.toLowerCase() !== 'plan adulto fundador'
        );
        this.cargandoPlanes = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error al cargar planes:', err);
        this.cargandoPlanes = false;
        this.cdr.detectChanges();
      }
    });
  }

  getBeneficiosList(beneficios: string): string[] {
    if (!beneficios) return [];
    return beneficios.split('\n').filter(b => b.trim() !== '');
  }
}
