# Model problem

We consider $\Omega=[-1,1]$. Find $\mathbf{u} : \Omega \subset \mathbb{R}^2  \rightarrow \mathbb{R}^3$ such that 

$$
\begin{cases}
\nabla\mathbf{u}^T\mathbf{u} = \mathbf{I}_2 & \text{in}\ \Omega, \\
\mathbf{u} =\mathbf{g} & \text{on} \ \partial \Omega,
\end{cases}
$$ 

we can expand with $\mathbf{u} = [u_1, u_2,u_3]^T$

$$
\begin{cases}
\left(\frac{\partial u_1}{\partial x_1} \right)^2 + \left(\frac{\partial u_2}{\partial x_1} \right)^2+  \left(\frac{\partial u_3}{\partial x_1} \right)^2=1
& \text{in} \ \Omega,\\
\left(\frac{\partial u_1}{\partial x_2} \right)^2 + \left(\frac{\partial u_2}{\partial x_2} \right)^2+  \left(\frac{\partial u_3}{\partial x_2} \right)^2=1 
& \text{in} \ \Omega,\\
\frac{\partial u_1}{\partial x_1}\frac{\partial u_1}{\partial x_2}  + \frac{\partial u_2}{\partial x_1}\frac{\partial u_2}{\partial x_2}+ \frac{\partial u_3}{\partial x_1}\frac{\partial u_3}{\partial x_2}=0
& \text{in} \ \Omega,\\
\mathbf{u}=\mathbf{g} & \text{on} \ \partial \Omega.
\end{cases}
$$

# PINN problem solution





# Numerical results

We consider a test case where

$ \left( \begin{array}{c} x_1 \\   \textrm{sign}(x_2) (1-\cos(x_2))   \\ \sin(\vert x_2\vert )$

$$
\mathbf{g}(x_1,x_2) = \left( \begin{array}{c} x_1 \\   \textrm{sign}(x_2) (1-\cos(x_2))   \\ \sin(\vert x_2\vert )     \end{array} \right), 
\quad \forall (x_1,x_2) \in \Omega.
$$ 
%

The Figure bellow shows the numerical solution of rigit maps equations for the given boundary conditions  
![surf_solution2](https://user-images.githubusercontent.com/49443913/209683046-72002bf0-68f5-45ae-be4e-290270498fb0.png)





