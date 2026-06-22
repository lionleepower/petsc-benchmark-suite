#include <petscksp.h>

int main(int argc, char **argv)
{
  Mat         A;
  Vec         u, b, x;
  KSP         ksp;
  PetscInt    m = 4, n = 4, p = 4;
  PetscInt    Istart, Iend, Ii, i, j, k, J, K;
  PetscScalar v;
  PetscReal   norm;

  PetscCall(PetscInitialize(&argc, &argv, NULL, NULL));

  /*
    Build an (m*n*p) x (m*n*p) sparse matrix for the seven-point stencil.
  */
  PetscCall(MatCreate(PETSC_COMM_WORLD, &A));
  PetscCall(MatSetSizes(A, PETSC_DECIDE, PETSC_DECIDE, m * n * p, m * n * p));
  PetscCall(MatSetFromOptions(A));
  PetscCall(MatMPIAIJSetPreallocation(A, 7, NULL, 7, NULL));
  PetscCall(MatSeqAIJSetPreallocation(A, 7, NULL));

  PetscCall(MatGetOwnershipRange(A, &Istart, &Iend));

  for (Ii = Istart; Ii < Iend; Ii++) {
    i = Ii % m;
    j = (Ii / m) % n;
    k = Ii / (m * n);
    v = -1.0;


    // Left neighbor: (i-1, j, k) 
    if (i > 0) {
      J = Ii - 1;
      PetscCall(MatSetValues(A, 1, &Ii, 1, &J, &v, INSERT_VALUES));
    }

    // Right neighbor: (i+1, j, k)
    if (i < m - 1) {
      J = Ii + 1;
      PetscCall(MatSetValues(A, 1, &Ii, 1, &J, &v, INSERT_VALUES));
    }

    // Up neighbor: (i, j-1, k)
    if (j > 0) {
      J = Ii - m;
      PetscCall(MatSetValues(A, 1, &Ii, 1, &J, &v, INSERT_VALUES));
    }


    // Down neighbor: (i, j+1, k) 
    if (j < n - 1) {
      J = Ii + m;
      PetscCall(MatSetValues(A, 1, &Ii, 1, &J, &v, INSERT_VALUES));
    }


    // Back neighbor: (i, j, k+1)
    if (k > 0) {
      K = Ii - m * n;
      PetscCall(MatSetValues(A, 1, &Ii, 1, &K, &v, INSERT_VALUES));
    }

    // Front neighbor: (i, j, k-1)
    if (k < p - 1) {
      K = Ii + m * n;
      PetscCall(MatSetValues(A, 1, &Ii, 1, &K, &v, INSERT_VALUES));
    }



    v = 6.0;
    PetscCall(MatSetValues(A, 1, &Ii, 1, &Ii, &v, INSERT_VALUES));
  }

  PetscCall(MatAssemblyBegin(A, MAT_FINAL_ASSEMBLY));
  PetscCall(MatAssemblyEnd(A, MAT_FINAL_ASSEMBLY));

  PetscCall(VecCreate(PETSC_COMM_WORLD, &u));
  PetscCall(VecSetSizes(u, PETSC_DECIDE, m * n * p));
  PetscCall(VecSetFromOptions(u));
  PetscCall(VecDuplicate(u, &b));
  PetscCall(VecDuplicate(u, &x));

  /*
    Pick the exact solution u = 1 and build b = A*u.
  */
  PetscCall(VecSet(u, 1.0));
  PetscCall(MatMult(A, u, b));

  PetscCall(KSPCreate(PETSC_COMM_WORLD, &ksp));
  PetscCall(KSPSetOperators(ksp, A, A));
  PetscCall(KSPSetFromOptions(ksp));
  PetscCall(KSPSolve(ksp, b, x));

  /*
    Compute the error norm ||x - u||_2.
  */
  PetscCall(VecAXPY(x, -1.0, u));
  PetscCall(VecNorm(x, NORM_2, &norm));
  PetscCall(PetscPrintf(PETSC_COMM_WORLD, "3d stencil error norm: %g\n", (double)norm));

  PetscCall(KSPDestroy(&ksp));
  PetscCall(VecDestroy(&u));
  PetscCall(VecDestroy(&b));
  PetscCall(VecDestroy(&x));
  PetscCall(MatDestroy(&A));
  PetscCall(PetscFinalize());
  return 0;
}
