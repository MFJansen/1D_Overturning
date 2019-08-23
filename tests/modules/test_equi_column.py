import pytest
import sys
import inspect
import numpy as np
from numpy import testing
sys.path.append('/pymoc/src/modules')
from equi_column import Equi_Column

@pytest.fixture(scope="module", params=[
  {
    'z': np.asarray(np.linspace(-4000, 0, 80)),
    'B_int': 3e3,
    'A': 2.0e14,
    'kappa': 3e-5,
    'H': 500.0
  },
  {
    'z': np.asarray(np.linspace(-4000, 0, 80)),
    'B_int': 3e3,
    'A': 2.0e14,
    'kappa': np.asarray(np.linspace(3e-5, 1e-5, 80)),
    'dkappa_dz': lambda z: -1e-7 * z / 4e3,
    'H': 500.0
  },
  {
    'z': np.asarray(np.linspace(-4000, 0, 80)),
    'B_int': 3e3,
    'A': 2.0e14,
    'kappa': lambda z: -3e-5 * z / 4e3,
    'H': 500.0
  },
  {
    'z': np.asarray(np.linspace(-4000, 0, 80)),
    'B_int': 3e3,
    'A': 2.0e14,
    'kappa': lambda z: -3e-5 * z / 4e3,
    'dkappa_dz': lambda z: -1e-7 * z / 4e3,
    'H': 500.0
  },
  {
    'z': np.asarray(np.linspace(-4000, 0, 80)),
    'B_int': 3e3,
    'A': 2.0e14,
    'psi_so': np.asarray((np.linspace(-4000, 0, 80) + 2000)**2),
    'H': 500.0
  },
  {
    'z': np.asarray(np.linspace(-4000, 0, 80)),
    'B_int': 3e3,
    'A': 2.0e14,
    'psi_so': lambda z: np.asarray((z/2) + 2000)**2,
    'H': 500.0
  },
  {
    'z': np.asarray(np.linspace(-4000, 0, 80)),
    'B_int': 3e3,
    'A': 2.0e14,
    'psi_so': 100,
    'H': 500.0
  },
  {
    'z': np.asarray(np.linspace(-4000, 0, 80)),
    'A': 2.0e14,
    'kappa': 3e-5,
    'H': 500.0,
    'B_int': None,
    'b_bot': None,
  },
  {
    'z': np.asarray(np.linspace(-4000, 0, 80)),
    'A': 2.0e14,
    'kappa': 3e-5,
    'H': 500.0,
    'B_int': None,
    'b_bot': 4e3,
  },
  {
    'z': np.asarray(np.linspace(-4000, 0, 80)),
    'A': 2.0e14,
    'kappa': 3e-5,
    'H': 500.0,
    'b_s': 0.05,
  },
  {
    'z': np.asarray(np.linspace(-4000, 0, 80)),
    'A': 2.0e14,
    'kappa': 3e-5,
    'H': 500.0,
    'sol_init': np.sin(np.asarray(np.linspace(-4000, 0, 80)))**2,
  },
])
def column_config(request):
  return request.param

@pytest.fixture(scope="module")
def column(request):
  return Equi_Column(**{
    'z': np.asarray(np.linspace(-4000, 0, 80)),
    'B_int': 3e3,
    'A': 2.0e14,
    'kappa': 3e-5
  })

class TestEqui_Column(object):
  def test_Equi_Column_init(self, column_config):
    if 'B_int' in column_config and not column_config['B_int'] and 'b_bot' in column_config and not column_config['b_bot']:
      with pytest.raises(Exception) as binfo:
        Equi_Column(**column_config)
      assert(str(binfo.value) == "You need to specify either b_bot or B_int for bottom boundary condition")
      return
    column_signature = inspect.signature(Equi_Column)

    column = Equi_Column(**column_config)

    for k in ['f', 'A', 'H', 'H_guess']:
      assert getattr(column, k)  == (column_config[k] if k in column_config and column_config[k] else column_signature.parameters[k].default)
    for k in ['z']:
      testing.assert_array_equal(getattr(column, k), (column_config[k] if k in column_config and not column_config[k] is None else column_signature.parameters[k].default))

    if not 'B_int' in column_config or not column_config['B_int'] is None:
      if 'B_int' in column_config:
        assert column.B_int == column_config['B_int']
      else:
        assert column.B_int == column_signature.parameters['B_int'].default

    if 'B_int' in column_config and not column_config['B_int']:
      assert column.b_bot == -column_config['b_bot'] / column.f**2

    if not 'b_s' in column_config or not column_config['b_s'] is None:
      if 'b_s' in column_config:
        assert column.bs == -column_config['b_s'] / column.f**2
      else:
        assert column.bs == -column_signature.parameters['b_s'].default / column.f**2

    nz = column_config['nz'] if 'nz' in column_config and not column_config['nz'] is None else 100
    for i in range(nz):
      testing.assert_approx_equal(column.zi[i], i/(nz - 1) - 1)

    assert callable(column.kappa)
    assert callable(column.dkappa_dz)
    if 'kappa' in column_config and not column_config['kappa'] is None:
      if callable(column_config['kappa']):
        for z in column_config['z']:
          assert column.kappa(z, 1.0) == column_config['kappa'](z) / (column.f)
          if 'dkappa_dz' in column_config and callable(column_config['dkappa_dz']):
            assert column.dkappa_dz(z, 1.0) == column_config['dkappa_dz'](z) / (column.f)
          # This case may not currently be functional
          # else:
          #   testing.assert_approx_equal(column.dkappa_dz(z, 1.0), (column_config['kappa'](column_config['z'][1]) - column_config['kappa'](column_config['z'][0])) / (column.f*(column_config['z'][1] - column_config['z'][0])))
      elif isinstance(column_config['kappa'], np.ndarray):
        for i in range(len(column_config['z'])):
          assert column.kappa(column_config['z'][i], 1.0) == column_config['kappa'][i] / (column.f)
          testing.assert_approx_equal(column.dkappa_dz(column_config['z'][i], 1.0), (column_config['kappa'][1] - column_config['kappa'][0]) / (column.f*(column_config['z'][1] - column_config['z'][0])))
      else:
        for z in column_config['z']:
          assert column.kappa(z, 200.0) == column_config['kappa'] / (4e4*column.f)
          assert column.dkappa_dz(z, 200.0) == 0

    if 'psi_so' in column_config and not column_config['psi_so'] is None:
      if callable(column_config['psi_so']):
        for z in column_config['z']:
          assert column.psi_so(z, 1.0) == column_config['psi_so'](z) / (column.f)
      elif isinstance(column_config['psi_so'], np.ndarray):
        for i in range(len(column_config['z'])):
          assert column.psi_so(column_config['z'][i], 1.0) == column_config['psi_so'][i] / (column.f)
      else:
        for z in column_config['z']:
          assert column.psi_so(z, 100) == 0
    else:
      for z in column_config['z']:
        assert column.psi_so(z, 100) == 0

    if 'sol_init' in column_config and not column_config['sol_init'] is None:
      assert all(column.sol_init == column_config['sol_init'])
    else:
      for i in range(len(column.z)):
        assert column.sol_init[0,i] == 1
        assert column.sol_init[2,i] == 0
        if 'b_bot' in column_config and column_config['b_bot'] is not None:
          assert column.sol_init[3,i] == -100
        else:
          assert column.sol_init[3,i] == -column.bz(1500)



  def test_alpha(self, column):
    for z in column.z:
      assert column.alpha(z, 1200) == 1200**2 / (column.A * column.kappa(z, 1200))

  def test_bz(self, column):
    assert column.bz(1200) == column.B_int / (column.f**3 * 1200**2 * column.A * column.kappa(-1, 1200))

  def test_bc(self, column):
    ya = [1, 2, 3, 4]
    yb = [11, 12, 13, 14]
    p = [100]
    bc = column.bc(ya, yb, p)
    assert bc[0] == 1
    assert bc[1] == 11
    assert bc[2] == 2
    assert bc[3] == 4 + column.bz(100)

  def test_ode(self):
    return 

  def test_solve(self):
    return 