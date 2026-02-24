import type { Conversation } from '@/types/api'

function daysAgo(n: number, hours = 10): string {
  const d = new Date()

  d.setDate(d.getDate() - n)
  d.setHours(hours, 0, 0, 0)

  return d.toISOString()
}

export const DEMO_CONVERSATIONS: Conversation[] = [
  // ── Seed 001: Consulta de vehículo nuevo ──
  {
    conversation_id: 'demo-conv-001',
    seed_id: 'demo-seed-001',
    dominio: 'automotive.sales',
    idioma: 'es',
    es_sintetica: true,
    created_at: daysAgo(6, 9),
    metadata: { generation_model: 'claude-3.5-sonnet', temperature: 0.7 },
    turnos: [
      {
        turno: 1,
        rol: 'cliente',
        contenido: 'Buenos días, estoy buscando un SUV para mi familia. Somos 5 y necesitamos algo espacioso pero que no consuma demasiado.',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 2,
        rol: 'asesor_ventas',
        contenido: 'Buenos días, bienvenido. Con mucho gusto le ayudo. Para una familia de 5 personas, tenemos excelentes opciones en SUVs medianas y grandes. ¿Tiene algún rango de presupuesto en mente?',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 3,
        rol: 'cliente',
        contenido: 'Estaba pensando en algo entre 600 y 900 mil pesos. ¿Qué opciones tienen?',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 4,
        rol: 'asesor_ventas',
        contenido: 'Excelente rango. En ese presupuesto tenemos tres opciones muy competitivas. Permítame consultar la disponibilidad actual en nuestro inventario.',
        herramientas_usadas: ['inventory_lookup'],
        metadata: {}
      },
      {
        turno: 5,
        rol: 'asesor_ventas',
        contenido: 'Tenemos disponibles: el Modelo XR5 2025 desde $689,900, el Modelo Atlas Pro 2024 desde $749,000, y el Modelo Terrain LX 2025 desde $825,000. Los tres ofrecen tercera fila de asientos y excelente rendimiento de combustible. ¿Le gustaría que comparemos las características de alguno en particular?',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 6,
        rol: 'cliente',
        contenido: 'El XR5 y el Atlas Pro me interesan. ¿Cuál tiene mejor espacio de carga?',
        herramientas_usadas: [],
        metadata: {}
      }
    ]
  },
  {
    conversation_id: 'demo-conv-002',
    seed_id: 'demo-seed-001',
    dominio: 'automotive.sales',
    idioma: 'es',
    es_sintetica: true,
    created_at: daysAgo(5, 14),
    metadata: { generation_model: 'claude-3.5-sonnet', temperature: 0.7 },
    turnos: [
      {
        turno: 1,
        rol: 'cliente',
        contenido: 'Hola, vi en su página que tienen SUVs en promoción. Me interesa algo con tracción integral.',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 2,
        rol: 'asesor_ventas',
        contenido: 'Hola, así es. Tenemos varias opciones con tracción integral. Déjeme consultar qué tenemos disponible en este momento.',
        herramientas_usadas: ['inventory_lookup'],
        tool_calls: [
          {
            tool_call_id: 'tc-001',
            tool_name: 'inventory_lookup',
            arguments: { category: 'suv', price_range: 'medio' }
          }
        ],
        tool_results: [
          {
            tool_call_id: 'tc-001',
            tool_name: 'inventory_lookup',
            status: 'success',
            duration_ms: 340,
            result: {
              vehicles: [
                { model: 'XR5 AWD 2025', price: 729900, stock: 3, colors: ['blanco', 'gris', 'negro'] },
                { model: 'Atlas Pro AWD 2024', price: 789000, stock: 2, colors: ['azul', 'blanco'] },
                { model: 'Terrain LX AWD 2025', price: 869000, stock: 1, colors: ['negro'] }
              ]
            }
          }
        ],
        metadata: {}
      },
      {
        turno: 3,
        rol: 'asesor_ventas',
        contenido: 'Tenemos tres modelos con tracción integral disponibles: el XR5 AWD 2025 desde $729,900 en tres colores, el Atlas Pro AWD 2024 a $789,000, y el Terrain LX AWD 2025 a $869,000. ¿Cuál le llama más la atención?',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 4,
        rol: 'cliente',
        contenido: 'El XR5 AWD suena bien. ¿Pueden darme el precio final con todo incluido?',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 5,
        rol: 'asesor_ventas',
        contenido: 'Claro, permítame calcular el precio final con impuestos y derechos vehiculares.',
        herramientas_usadas: ['price_calculator'],
        tool_calls: [
          {
            tool_call_id: 'tc-002',
            tool_name: 'price_calculator',
            arguments: { model_id: 'xr5-awd-2025', options: ['paquete-seguridad'] }
          }
        ],
        tool_results: [
          {
            tool_call_id: 'tc-002',
            tool_name: 'price_calculator',
            status: 'success',
            duration_ms: 210,
            result: {
              base_price: 729900,
              options_total: 15000,
              subtotal: 744900,
              iva: 119184,
              total: 864084,
              breakdown: { tenencia: 0, placas: 4500, verificacion: 850 }
            }
          }
        ],
        metadata: {}
      },
      {
        turno: 6,
        rol: 'asesor_ventas',
        contenido: 'El precio final del XR5 AWD 2025 con paquete de seguridad incluido es de $864,084 MXN, que incluye IVA, placas y verificación. ¿Le gustaría agendar una prueba de manejo?',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 7,
        rol: 'cliente',
        contenido: 'Sí, me gustaría probarlo este fin de semana si es posible.',
        herramientas_usadas: [],
        metadata: {}
      }
    ]
  },

  // ── Seed 002: Prueba de manejo ──
  {
    conversation_id: 'demo-conv-003',
    seed_id: 'demo-seed-002',
    dominio: 'automotive.sales',
    idioma: 'es',
    es_sintetica: true,
    created_at: daysAgo(5, 11),
    metadata: { generation_model: 'claude-3.5-sonnet', temperature: 0.7 },
    turnos: [
      {
        turno: 1,
        rol: 'cliente',
        contenido: 'Hola, hablé con un asesor la semana pasada y me gustaría agendar una prueba de manejo del XR5.',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 2,
        rol: 'coordinador_pruebas',
        contenido: '¡Excelente elección! El XR5 es uno de nuestros modelos más populares. ¿Tiene alguna preferencia de fecha y horario?',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 3,
        rol: 'cliente',
        contenido: 'El sábado por la mañana sería ideal para mí.',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 4,
        rol: 'coordinador_pruebas',
        contenido: 'Perfecto. Le confirmo que tenemos disponibilidad el sábado a las 10:00 AM. Recuerde traer su licencia de conducir vigente. La prueba tiene una duración de aproximadamente 30 minutos por una ruta predeterminada. ¿Le confirmo la cita?',
        herramientas_usadas: ['appointment_scheduler'],
        metadata: {}
      },
      {
        turno: 5,
        rol: 'cliente',
        contenido: 'Sí, confirmo. ¿Necesito algo más además de la licencia?',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 6,
        rol: 'coordinador_pruebas',
        contenido: 'Solo la licencia vigente. Queda confirmada su cita para el sábado a las 10:00 AM para prueba de manejo del XR5. Le enviaremos un recordatorio. ¡Lo esperamos!',
        herramientas_usadas: [],
        metadata: {}
      }
    ]
  },
  {
    conversation_id: 'demo-conv-004',
    seed_id: 'demo-seed-002',
    dominio: 'automotive.sales',
    idioma: 'es',
    es_sintetica: false,
    created_at: daysAgo(4, 16),
    metadata: { source: 'whatsapp_export', imported_by: 'parser_v1' },
    turnos: [
      {
        turno: 1,
        rol: 'cliente',
        contenido: 'Buenas tardes, quisiera reprogramar mi prueba de manejo. Tenía cita para mañana pero surgió un imprevisto.',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 2,
        rol: 'coordinador_pruebas',
        contenido: 'Sin problema. ¿Para qué día le gustaría reprogramar?',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 3,
        rol: 'cliente',
        contenido: 'El próximo martes o miércoles, por favor.',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 4,
        rol: 'coordinador_pruebas',
        contenido: 'El martes tenemos disponibilidad a las 11:00 AM y a las 3:00 PM. El miércoles a las 9:00 AM. ¿Cuál le conviene mejor?',
        herramientas_usadas: ['appointment_scheduler'],
        metadata: {}
      },
      {
        turno: 5,
        rol: 'cliente',
        contenido: 'El martes a las 3 PM está perfecto.',
        herramientas_usadas: [],
        metadata: {}
      }
    ]
  },

  // ── Seed 003: Trade-in ──
  {
    conversation_id: 'demo-conv-005',
    seed_id: 'demo-seed-003',
    dominio: 'automotive.sales',
    idioma: 'es',
    es_sintetica: true,
    created_at: daysAgo(4, 10),
    metadata: { generation_model: 'claude-3.5-sonnet', temperature: 0.7 },
    turnos: [
      {
        turno: 1,
        rol: 'cliente',
        contenido: 'Hola, me interesa cambiar mi camioneta actual por un modelo más nuevo. ¿Manejan programa de trade-in?',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 2,
        rol: 'valuador',
        contenido: 'Sí, contamos con un programa de trade-in. Para darle una valuación inicial, necesito algunos datos de su vehículo actual. ¿Me puede compartir la marca, modelo, año y kilometraje aproximado?',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 3,
        rol: 'cliente',
        contenido: 'Es un Modelo Frontier 2020, tiene como 65,000 kilómetros. Está en buenas condiciones, siempre le hice servicio en agencia.',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 4,
        rol: 'valuador',
        contenido: 'Excelente. Si tiene el número VIN a la mano, puedo hacer una valuación más precisa. Está en la tarjeta de circulación o en la base del parabrisas.',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 5,
        rol: 'cliente',
        contenido: 'Sí, es 1N6AD0CW5LC823456.',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 6,
        rol: 'valuador',
        contenido: 'Perfecto, déjeme verificar los datos del vehículo y hacer la estimación de valor.',
        herramientas_usadas: ['vin_decoder', 'trade_in_estimator'],
        tool_calls: [
          {
            tool_call_id: 'tc-003',
            tool_name: 'vin_decoder',
            arguments: { vin: '1N6AD0CW5LC823456' }
          }
        ],
        tool_results: [
          {
            tool_call_id: 'tc-003',
            tool_name: 'vin_decoder',
            status: 'success',
            duration_ms: 520,
            result: {
              year: 2020,
              make: 'Nissan',
              model: 'Frontier Pro-4X',
              engine: '3.8L V6',
              transmission: 'Automática 9 velocidades',
              drivetrain: '4WD'
            }
          }
        ],
        metadata: {}
      },
      {
        turno: 7,
        rol: 'valuador',
        contenido: 'Según los datos del VIN, su vehículo es un Frontier Pro-4X 2020 con motor 3.8L V6 y tracción 4WD. Basado en el kilometraje y condición reportada, el valor estimado de trade-in está entre $295,000 y $320,000 MXN. Esta valuación es válida por 7 días y está sujeta a una inspección física. ¿Le gustaría agendar la inspección?',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 8,
        rol: 'cliente',
        contenido: 'Sí, me parece razonable. ¿Cuándo podría traerla?',
        herramientas_usadas: [],
        metadata: {}
      }
    ]
  },
  {
    conversation_id: 'demo-conv-006',
    seed_id: 'demo-seed-003',
    dominio: 'automotive.sales',
    idioma: 'es',
    es_sintetica: true,
    created_at: daysAgo(3, 11),
    metadata: { generation_model: 'claude-3.5-sonnet', temperature: 0.7 },
    turnos: [
      {
        turno: 1,
        rol: 'cliente',
        contenido: 'Hola, tengo un sedán 2019 que me gustaría dejar como enganche para un vehículo nuevo. ¿Es posible?',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 2,
        rol: 'valuador',
        contenido: 'Por supuesto, ese es precisamente nuestro programa de trade-in. ¿Me puede dar los datos de su vehículo? Marca, modelo, año y kilómetros.',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 3,
        rol: 'cliente',
        contenido: 'Es un Modelo Corsa 2019, como 80,000 km, condición regular, tiene unos rayones menores.',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 4,
        rol: 'valuador',
        contenido: 'Entendido. Basado en los datos que me comparte, la estimación inicial está en el rango de $185,000 a $210,000 MXN. Los detalles cosméticos se evalúan en la inspección física y pueden ajustar el valor. ¿Quiere que procedamos con la inspección formal?',
        herramientas_usadas: ['trade_in_estimator'],
        metadata: {}
      }
    ]
  },

  // ── Seed 004: Financiamiento ──
  {
    conversation_id: 'demo-conv-007',
    seed_id: 'demo-seed-004',
    dominio: 'automotive.sales',
    idioma: 'es',
    es_sintetica: true,
    created_at: daysAgo(3, 15),
    metadata: { generation_model: 'claude-3.5-sonnet', temperature: 0.7 },
    turnos: [
      {
        turno: 1,
        rol: 'cliente',
        contenido: 'Me interesa el XR5 AWD pero necesito financiamiento. ¿Qué opciones tienen?',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 2,
        rol: 'asesor_financiero',
        contenido: 'Con gusto le ayudo. Para ofrecerle las mejores opciones, necesito algunos datos: ¿cuánto podría dar de enganche y a cuántos meses le gustaría el financiamiento?',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 3,
        rol: 'cliente',
        contenido: 'Puedo dar como 200,000 de enganche. ¿A 48 meses cómo quedaría?',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 4,
        rol: 'asesor_financiero',
        contenido: 'Perfecto, déjeme hacer la simulación con esos datos.',
        herramientas_usadas: ['credit_calculator'],
        metadata: {}
      },
      {
        turno: 5,
        rol: 'asesor_financiero',
        contenido: 'Con un enganche de $200,000 y el precio del XR5 AWD de $864,084, el monto a financiar sería de $664,084. A 48 meses con tasa preferencial, su mensualidad quedaría aproximadamente en $17,250 MXN. También tenemos opción a 36 meses por $21,800 con menor costo financiero total. ¿Le gustaría ver ambas opciones en detalle?',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 6,
        rol: 'cliente',
        contenido: 'La de 48 meses me conviene más. ¿Qué documentos necesito para la pre-aprobación?',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 7,
        rol: 'asesor_financiero',
        contenido: 'Para la pre-aprobación necesita: identificación oficial vigente, comprobante de domicilio reciente, últimos 3 recibos de nómina, últimos 3 estados de cuenta bancarios y su RFC. Con esos documentos podemos tener respuesta en 24-48 horas.',
        herramientas_usadas: [],
        metadata: {}
      }
    ]
  },
  {
    conversation_id: 'demo-conv-008',
    seed_id: 'demo-seed-004',
    dominio: 'automotive.sales',
    idioma: 'es',
    es_sintetica: false,
    created_at: daysAgo(2, 10),
    metadata: { source: 'crm_export', imported_by: 'parser_v1' },
    turnos: [
      {
        turno: 1,
        rol: 'cliente',
        contenido: 'Buenas tardes, quiero saber si califico para financiamiento. Soy trabajador independiente.',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 2,
        rol: 'asesor_financiero',
        contenido: 'Buenas tardes. Claro, también tenemos esquemas para trabajadores independientes. ¿Cuál es su ingreso mensual aproximado y qué vehículo le interesa?',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 3,
        rol: 'cliente',
        contenido: 'Mi ingreso promedio es de unos 45,000 mensuales. Me interesa algo en el rango de 500,000.',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 4,
        rol: 'asesor_financiero',
        contenido: 'Permítame simular algunas opciones.',
        herramientas_usadas: ['credit_calculator'],
        tool_calls: [
          {
            tool_call_id: 'tc-004',
            tool_name: 'credit_calculator',
            arguments: { vehicle_price: 500000, down_payment: 100000, term_months: 48, credit_score: 'bueno' }
          }
        ],
        tool_results: [
          {
            tool_call_id: 'tc-004',
            tool_name: 'credit_calculator',
            status: 'success',
            duration_ms: 280,
            result: {
              monthly_payment: 11450,
              total_interest: 149600,
              total_cost: 549600,
              annual_rate: 14.9,
              insurance_monthly: 1850
            }
          }
        ],
        metadata: {}
      },
      {
        turno: 5,
        rol: 'asesor_financiero',
        contenido: 'Con un enganche de $100,000 y financiamiento a 48 meses, la mensualidad quedaría en aproximadamente $11,450 más seguro automotriz de $1,850 mensuales. Para independientes, los documentos son: últimas 2 declaraciones anuales, estados de cuenta de los últimos 6 meses y constancia de situación fiscal.',
        herramientas_usadas: [],
        metadata: {}
      }
    ]
  },

  // ── Seed 005: Servicio post-venta ──
  {
    conversation_id: 'demo-conv-009',
    seed_id: 'demo-seed-005',
    dominio: 'automotive.sales',
    idioma: 'es',
    es_sintetica: true,
    created_at: daysAgo(2, 15),
    metadata: { generation_model: 'claude-3.5-sonnet', temperature: 0.7 },
    turnos: [
      {
        turno: 1,
        rol: 'cliente',
        contenido: 'Hola, mi carro ya tiene 10,000 km y creo que le toca servicio. ¿Qué incluye?',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 2,
        rol: 'asesor_servicio',
        contenido: 'Buen día. El servicio de los 10,000 km es un mantenimiento menor que incluye cambio de aceite y filtro, revisión de frenos, rotación de llantas y diagnóstico electrónico. El costo es de $3,500 y tiene una duración aproximada de 2 horas.',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 3,
        rol: 'cliente',
        contenido: 'Perfecto. ¿Puedo llevarlo este viernes?',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 4,
        rol: 'asesor_servicio',
        contenido: 'Claro, tenemos disponibilidad el viernes. ¿Prefiere dejarlo temprano a las 7:00 AM o a media mañana? Si lo deja a las 7, estaría listo para las 9:30 aproximadamente.',
        herramientas_usadas: ['service_scheduler'],
        metadata: {}
      },
      {
        turno: 5,
        rol: 'cliente',
        contenido: 'A las 7 está bien, así paso por él antes del mediodía.',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 6,
        rol: 'asesor_servicio',
        contenido: 'Listo, queda agendado para este viernes a las 7:00 AM, servicio de 10,000 km. Recuerde traer su libreta de servicio. ¡Lo esperamos!',
        herramientas_usadas: [],
        metadata: {}
      }
    ]
  },
  {
    conversation_id: 'demo-conv-010',
    seed_id: 'demo-seed-005',
    dominio: 'automotive.sales',
    idioma: 'es',
    es_sintetica: false,
    created_at: daysAgo(1, 9),
    metadata: { source: 'whatsapp_export', imported_by: 'parser_v1' },
    turnos: [
      {
        turno: 1,
        rol: 'cliente',
        contenido: 'Hola, se me encendió una luz en el tablero, parece ser del motor. ¿Es urgente?',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 2,
        rol: 'asesor_servicio',
        contenido: 'Buenas tardes. La luz de check engine puede indicar varias cosas, desde algo menor como el tapón de gasolina hasta algo que requiera atención inmediata. Le recomendaría traerlo lo antes posible para un diagnóstico. ¿Nota algún comportamiento diferente en el vehículo?',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 3,
        rol: 'cliente',
        contenido: 'No, maneja normal. Pero prefiero no arriesgarme. ¿Tienen espacio mañana?',
        herramientas_usadas: [],
        metadata: {}
      },
      {
        turno: 4,
        rol: 'asesor_servicio',
        contenido: 'Si maneja normal probablemente no es urgente, pero es prudente revisarlo pronto. Tenemos espacio mañana a las 8:00 AM. El diagnóstico electrónico tiene un costo de $850 que se descuenta si se realiza la reparación. ¿Le agendo?',
        herramientas_usadas: ['service_scheduler'],
        metadata: {}
      },
      {
        turno: 5,
        rol: 'cliente',
        contenido: 'Sí, por favor agéndeme a las 8.',
        herramientas_usadas: [],
        metadata: {}
      }
    ]
  }
]
