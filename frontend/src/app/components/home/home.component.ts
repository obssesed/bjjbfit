import { Component, OnInit, ChangeDetectorRef, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService, PerfilDeportista, Plan } from '../../services/auth.service';
import { ClasesService, ClaseBJJ, Actividad, Producto, VideoRepaso } from '../../services/clases.service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  perfil: PerfilDeportista | null = null;
  activeTab: string = 'nosotros';
  videoMuted: boolean = true;
  proximasClases: ClaseBJJ[] = [];
  cargandoClases: boolean = true;

  // Actividades dinámicas
  actividades: Actividad[] = [];
  cargandoActividades: boolean = true;
  planes: Plan[] = [];
  cargandoPlanes: boolean = true;
  
  // Modal edición actividad
  mostrarModalActividad: boolean = false;
  actividadEdicion: any = {};
  archivoImagen: File | null = null;
  guardandoActividad: boolean = false;

  // Productos dinámicos
  productos: Producto[] = [];
  cargandoProductos: boolean = true;
  mostrarModalProducto: boolean = false;
  productoEdicion: any = {};
  archivoImagenProducto: File | null = null;
  guardandoProducto: boolean = false;

  // Vídeos de repaso
  videosRepaso: VideoRepaso[] = [];
  videoActivo: VideoRepaso | null = null;
  cargandoVideos: boolean = true;
  mostrarModalVideo: boolean = false;
  videoEdicion: any = {};
  archivoVideo: File | null = null;
  archivoMiniatura: File | null = null;
  guardandoVideo: boolean = false;

  // Modal Confirmación
  mostrarModalConfirmar: boolean = false;
  tituloConfirmar: string = '';
  mensajeConfirmar: string = '';
  callbackConfirmar: (() => void) | null = null;

  @ViewChild('videoAcademia') videoRef!: ElementRef<HTMLVideoElement>;

  constructor(
    private authService: AuthService, 
    private clasesService: ClasesService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    // Suscripción al perfil (que ya puede venir con datos cacheados)
    this.authService.userProfile$.subscribe(perfil => {
      if (perfil) {
        this.perfil = perfil;
        if (this.perfil.is_staff) {
          this.cargarNotificacionesAdmin();
        }
        this.cdr.detectChanges();
      }
    });

    // Forzar recarga desde el servidor para asegurar datos frescos
    this.authService.cargarPerfil().subscribe({
      error: (err) => {
        console.error('Error recargando perfil en Home:', err);
      }
    });

    this.cargarProximasClases();
    this.cargarActividades();
    this.cargarProductos();
    this.cargarVideosRepaso();
    this.cargarPlanes();
  }

  solicitudesPendientesCount: number = 0;

  cargarNotificacionesAdmin(): void {
    this.authService.getSolicitudesReseteoPendientes().subscribe({
      next: (res) => {
        this.solicitudesPendientesCount = res.length;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error cargando solicitudes pendientes:', err);
      }
    });
  }

  cargarProximasClases(): void {
    this.cargandoClases = true;
    this.clasesService.getClases().subscribe({
      next: (clases) => {
        const ahora = new Date();
        
        // 1. Determinar categorías de acceso permitidas para el usuario
        const categoriasPermitidas = new Set<string>();
        
        if (this.perfil) {
          // Categoría del propio usuario
          if (this.perfil.fecha_nacimiento) {
            categoriasPermitidas.add(this.obtenerCategoriaPorFecha(this.perfil.fecha_nacimiento));
          } else {
            categoriasPermitidas.add('ADULTO');
          }
          
          // Si tiene hijos asociados, puede ver sesiones infantiles y juveniles
          if (this.perfil.hijos_a_cargo && this.perfil.hijos_a_cargo.length > 0) {
            categoriasPermitidas.add('INFANTIL');
            categoriasPermitidas.add('JUVENIL');
          }

          // El administrador puede ver todas las próximas sesiones para supervisar
          if (this.perfil.is_staff) {
            categoriasPermitidas.add('ADULTO');
            categoriasPermitidas.add('JUVENIL');
            categoriasPermitidas.add('INFANTIL');
          }
        }

        // 2. Filtrar y ordenar
        this.proximasClases = clases
          .filter(c => {
            const esFutura = new Date(c.fecha_hora_inicio) > ahora;
            const esPermitida = categoriasPermitidas.has(c.categoria_acceso);
            return esFutura && esPermitida;
          })
          .sort((a, b) => new Date(a.fecha_hora_inicio).getTime() - new Date(b.fecha_hora_inicio).getTime())
          .slice(0, 3);

        this.cargandoClases = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error cargando próximas clases:', err);
        this.cargandoClases = false;
        this.cdr.detectChanges();
      }
    });
  }

  private obtenerCategoriaPorFecha(fechaStr: string): string {
    const today = new Date();
    const birthDate = new Date(fechaStr);
    let age = today.getFullYear() - birthDate.getFullYear();
    const m = today.getMonth() - birthDate.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    
    if (age < 14) return 'INFANTIL';
    if (age < 18) return 'JUVENIL';
    return 'ADULTO';
  }

  setTab(tab: string) {
    this.activeTab = tab;
    // Scroll suave al contenido tras cambiar de tab
    setTimeout(() => {
      const el = document.querySelector('.home-main');
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 50);
  }

  /** Nombre formateado para el hero */
  get nombreUsuario(): string {
    if (!this.perfil) return 'Deportista';
    return this.perfil.first_name?.trim() || this.perfil.username || 'Deportista';
  }

  /** Cinturón con primera letra en mayúscula */
  get cinturonFormateado(): string {
    if (!this.perfil?.cinturon) return 'Blanco';
    const c = this.perfil.cinturon.toLowerCase();
    return c.charAt(0).toUpperCase() + c.slice(1);
  }

  /** Ampliar vídeo a pantalla completa */
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

  /** Alternar mute/unmute del vídeo */
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

  // --- MÉTODOS ADMIN ACTIVIDADES ---
  
  get isAdmin(): boolean {
    return this.perfil?.is_staff || false;
  }

  abrirModalActividad(actividad?: Actividad) {
    if (actividad) {
      this.actividadEdicion = { ...actividad };
    } else {
      this.actividadEdicion = {
        titulo: '',
        descripcion: '',
        badge: 'TÉCNICA',
        orden: this.actividades.length + 1
      };
    }
    this.archivoImagen = null;
    this.mostrarModalActividad = true;
  }

  cerrarModal() {
    this.mostrarModalActividad = false;
    this.actividadEdicion = {};
  }

  onFileSelected(event: any) {
    const file: File = event.target.files[0];
    if (file) {
      this.archivoImagen = file;
    }
  }

  guardarActividad() {
    if (!this.actividadEdicion.titulo || !this.actividadEdicion.descripcion) return;

    this.guardandoActividad = true;
    const payload = { ...this.actividadEdicion };
    if (this.archivoImagen) {
      payload.imagen = this.archivoImagen;
    } else {
      delete payload.imagen; // No enviar si no hay cambio o es URL
    }

    this.clasesService.guardarActividad(payload).subscribe({
      next: () => {
        this.guardandoActividad = false;
        this.cerrarModal();
        this.cargarActividades();
      },
      error: (err) => {
        console.error('Error al guardar actividad:', err);
        this.guardandoActividad = false;
        this.cdr.detectChanges();
      }
    });
  }

  eliminarActividad(id: number, event: Event) {
    event.stopPropagation();
    this.tituloConfirmar = 'Eliminar Actividad';
    this.mensajeConfirmar = '¿Estás seguro de que deseas eliminar esta actividad? Esta acción no se puede deshacer.';
    this.callbackConfirmar = () => {
      this.clasesService.eliminarActividad(id).subscribe({
        next: () => {
          this.cargarActividades();
          this.cerrarModalConfirmar();
        },
        error: (err) => console.error('Error al eliminar:', err)
      });
    };
    this.mostrarModalConfirmar = true;
  }

  // --- MÉTODOS CONFIRMACIÓN ---

  cerrarModalConfirmar() {
    this.mostrarModalConfirmar = false;
    this.callbackConfirmar = null;
  }

  ejecutarConfirmacion() {
    if (this.callbackConfirmar) {
      this.callbackConfirmar();
    }
    this.cerrarModalConfirmar();
  }

  cargarPlanes() {
    this.cargandoPlanes = true;
    this.authService.getPlanes().subscribe({
      next: (res: Plan[]) => {
        this.planes = res.filter(p => p.activo);
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

  // --- MÉTODOS ADMIN PRODUCTOS ---

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

  abrirModalProducto(producto?: Producto) {
    if (producto) {
      this.productoEdicion = { ...producto };
    } else {
      this.productoEdicion = {
        nombre: '',
        descripcion: '',
        tallas: '',
        estado_stock: 'IN_STOCK',
        orden: this.productos.length + 1
      };
    }
    this.archivoImagenProducto = null;
    this.mostrarModalProducto = true;
  }

  cerrarModalProducto() {
    this.mostrarModalProducto = false;
    this.productoEdicion = {};
  }

  onFileSelectedProducto(event: any) {
    const file: File = event.target.files[0];
    if (file) {
      this.archivoImagenProducto = file;
    }
  }

  guardarProducto() {
    if (!this.productoEdicion.nombre) return;

    this.guardandoProducto = true;
    const payload = { ...this.productoEdicion };
    if (this.archivoImagenProducto) {
      payload.imagen = this.archivoImagenProducto;
    } else {
      delete payload.imagen;
    }

    this.clasesService.guardarProducto(payload).subscribe({
      next: () => {
        this.guardandoProducto = false;
        this.cerrarModalProducto();
        this.cargarProductos();
      },
      error: (err) => {
        console.error('Error al guardar producto:', err);
        this.guardandoProducto = false;
        this.cdr.detectChanges();
      }
    });
  }

  eliminarProducto(id: number, event: Event) {
    event.stopPropagation();
    this.tituloConfirmar = 'Eliminar Producto';
    this.mensajeConfirmar = '¿Estás seguro de que deseas eliminar este producto de la tienda?';
    this.callbackConfirmar = () => {
      this.clasesService.eliminarProducto(id).subscribe({
        next: () => {
          this.cargarProductos();
          this.cerrarModalConfirmar();
        },
        error: (err) => console.error('Error al eliminar:', err)
      });
    };
    this.mostrarModalConfirmar = true;
  }

  // --- MÉTODOS VÍDEOS DE REPASO ---

  cargarVideosRepaso() {
    this.cargandoVideos = true;
    this.clasesService.getVideosRepaso().subscribe({
      next: (data) => {
        this.videosRepaso = data;
        if (this.videosRepaso.length > 0 && !this.videoActivo) {
          this.videoActivo = this.videosRepaso[0];
        }
        this.cargandoVideos = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error al cargar vídeos:', err);
        this.cargandoVideos = false;
        this.cdr.detectChanges();
      }
    });
  }

  seleccionarVideo(video: VideoRepaso) {
    this.videoActivo = video;
    this.cdr.detectChanges();
  }

  abrirModalVideo(video?: VideoRepaso) {
    if (video) {
      this.videoEdicion = { ...video };
    } else {
      this.videoEdicion = {
        titulo: '',
        descripcion: '',
        orden: this.videosRepaso.length + 1
      };
    }
    this.archivoVideo = null;
    this.archivoMiniatura = null;
    this.mostrarModalVideo = true;
  }

  cerrarModalVideo() {
    this.mostrarModalVideo = false;
    this.videoEdicion = {};
  }

  onFileSelectedVideo(event: any, type: 'video' | 'miniatura') {
    const file: File = event.target.files[0];
    if (file) {
      if (type === 'video') this.archivoVideo = file;
      else this.archivoMiniatura = file;
    }
  }

  guardarVideo() {
    if (!this.videoEdicion.titulo) return;

    // Validación básica de tamaño en el cliente (ej: 100MB)
    const MAX_SIZE = 100 * 1024 * 1024;
    if (this.archivoVideo && this.archivoVideo.size > MAX_SIZE) {
      alert('El vídeo es demasiado grande (máximo 100MB para el servidor local).');
      return;
    }

    this.guardandoVideo = true;
    console.log('Iniciando subida de vídeo...');
    
    const payload = { ...this.videoEdicion };
    if (this.archivoVideo) payload.archivo_video = this.archivoVideo;
    if (this.archivoMiniatura) payload.miniatura = this.archivoMiniatura;

    this.clasesService.guardarVideoRepaso(payload).subscribe({
      next: (res) => {
        console.log('Vídeo subido con éxito:', res);
        this.guardandoVideo = false;
        this.cerrarModalVideo();
        this.cargarVideosRepaso();
      },
      error: (err) => {
        console.error('Error detallado al guardar vídeo:', err);
        let msg = 'Error al subir el vídeo.';
        if (err.status === 413) msg = 'El vídeo es demasiado pesado para el servidor.';
        alert(msg);
        this.guardandoVideo = false;
        this.cdr.detectChanges();
      }
    });
  }

  eliminarVideo(id: number, event: Event) {
    event.stopPropagation();
    this.tituloConfirmar = 'Eliminar Vídeo';
    this.mensajeConfirmar = '¿Estás seguro de que deseas eliminar este vídeo de repaso?';
    this.callbackConfirmar = () => {
      this.clasesService.eliminarVideoRepaso(id).subscribe({
        next: () => {
          this.cargarVideosRepaso();
          this.cerrarModalConfirmar();
        },
        error: (err) => console.error('Error al eliminar vídeo:', err)
      });
    };
    this.mostrarModalConfirmar = true;
  }
}
