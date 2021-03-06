import numpy as np
from component import Component
import _simple_physics_custom as phys
from grid import Grid

class simple_physics_custom(Component):
    """
    Interface to the simple physics package. This is a modified version which allows the
    user to switch off any of the three routines : large scale condensation, surface fluxes,
    or boundary layer parameterisation
    
    Reed and Jablonowski 2012: 
    title = {Idealized tropical cyclone simulations of intermediate complexity: a test case for {AGCMs}}
	journal = {Journal of Advances in Modeling Earth Systems}

    Instantiation
    ============

    sp = climt.simple_physics(<args>)

    
    where <args> include the following REQUIRED arguments:
    Name           Dims         Meaning                        Units     Default                Notes

    grid            (object)     grid generated by by another
                                 component which is used to
                                 get latitudes for calculating
                                 the forcing

    dt              0            The (constant) time step to be  seconds
                                 used by the physics

    Ts              2            The surface temperature to use IF
                                 use_ext_ts is True (= 1)

    and the following OPTIONAL arguments (1 indicates True, use 0 for False):

    Name           Dims         Meaning                        Units     Default                Notes
    
    cyclone         0           Integer indicating if                    1
                                the physics must simulate
                                a cyclone. If 0, it
                                will simulate a moist baroclinic
                                environment. This option is used
                                only to generate surface temperatures.
                                This will be ignored if external 
                                surface temperatures are
                                prescribed

    lsc             0           Integer indicating whether
                                large scale condensation is active       1

    pbl             0           Integer indicating whether               1
                                boundary layer is active

    surf_flux       0           Integer indicating whether               1
                                surface fluxes are active

    use_ext_ts      0           Integer indicating whether               0
                                surface temperature is externally
                                specified (else internal default
                                corresponding to constant value
                                of 302.15 K is used)

    qflux           0           Integer indicating whether surface       1
                                latent heat fluxes are calculated

    momflux         0           Integer indicating whether surface       1
                                momentum fluxes are calculated

    tflux           0           Integer indicating whether surface       1
                                sensible heat fluxes are calculated


    Usage
    =====

    call instance directly to get increments

    inc = sp(<args>)

    where <args> are the following REQUIRED arguments:
    Name           Dims         Meaning                        Units     Default                Notes

    U               3           zonal winds                     ms-1

    V               3           meridional winds                ms-1

    T               3           temperature                     K

    p               3           atmospheric pressure            Pa

    pint            3           Pressure at model interfaces    Pa

    q               3           specific humidity               g kg-1
    
    ps              2           surface pressure                Pa


    * Outputs that are accessible as sp.<Name>
    Name           Dims         Meaning                        Units     Default                Notes

    Udot            3           zonal wind tendency             ms-2

    Vdot            3           meridional wind tendency        ms-2

    Tdot            3           temperature tendency            Ks-1

    qdot            3           humidity tendency               g kg-1

    precc           2           precipitation

    """

    def __init__(self, **kwargs):


        self.Name = 'simple_physics'
        self.LevType = 'p'
        self.SteppingScheme = 'explicit'
        self.ToExtension = ['U', 'V', 'T', 'p', 'pint', 'q', 'ps']
        self.Required = ['U', 'V', 'T', 'p', 'pint', 'q', 'ps']
        self.FromExtension = ['Uinc', 'Vinc', 'Tinc', 'qinc', 'precc']
        self.Prognostic = ['U', 'V', 'T', 'q']
        self.Diagnostic = ['precc']

        if 'grid' not in kwargs:
           kwargs['grid'] = Grid(self,**kwargs)


        time_step = 0
        if 'dt' not in kwargs:
            raise IndexError, '\n\n dt is a required argument'

        nlevs = kwargs['grid']['nlev']
        nlats = kwargs['grid']['nlat']
        nlons = kwargs['grid']['nlon']
        time_step = kwargs['dt']

        phys.init_simple_physics(1, nlons, nlats, nlevs, time_step, kwargs)

        Component.__init__(self,**kwargs)


    def driver(self, u, v, temp, p, pint, q, ps, simTime=-1):
        '''
        Returns the tendencies for a simplified moist physics simulation
        '''

        latitudes = self.Grid['lat']

        nlats = self.Grid['nlat']
        nlons = self.Grid['nlon']

        lons,lats,levs = u.shape

        assert lons == nlons
        assert lats == nlats

        u_tend = np.zeros(u.shape)
        v_tend = np.zeros(v.shape)
        t_tend = np.zeros(temp.shape)
        q_tend = np.zeros(q.shape)
        precip = np.zeros((nlons,nlats))



        t_out, u_out, v_out, q_out, precip_out = \
            phys.get_tendencies(u, v, temp,
                                  p, pint, q,
                                  ps, latitudes)


        return u_out,v_out,t_out,q_out,precip_out



