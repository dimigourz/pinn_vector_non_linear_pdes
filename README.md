# Model problem

We consider bounded domain 

Find $\mathbf{u} : \Omega \subset \mathbb{R}^2  \rightarrow \mathbb{R}^3$ such that 

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





#Numerical results


