function [Dep ] = ThetaDependence( component,m,n,theta )
%Texpresses the theta angular dependence of an outgoin spherical wave of
%indices m,n at a given theta
%component=1 for E_theta of s=1 modes
%component=2 for E_phi of s=1 modes
%component=3 for E_r of s=2 modes
%component=4 for E_theta of s=2 modes
%component=5 for E_phi of s=2 modes
%only works if theta is a scalar or a square matrix, not for vectors!!
constante=sqrt((n+0.5)*factorial(n-abs(m))/factorial(n+abs(m)));
Dep=theta*0;
theta0=theta==0;
thetapi=theta==pi;
thetaValido=~or(theta0,thetapi);
switch component
    case {1, 5}
        
        Dep(thetaValido)=1i*m*Pmn(abs(m),n,cos(theta(thetaValido)))./sin(theta(thetaValido));
  
        if abs(m)==1
        	signo=m/abs(m);
            Dep(theta0)=1i*constante*signo*n*(n+1)/2;
            Dep(thetapi)=1i*constante*signo*(-1)^(n+1)*n*(n+1)/2;
            
        else
            Dep(theta0)=0;
            Dep(thetapi)=0;
        end
      
    case {2,4}
        
       % Dep(thetaValido)=diffPmn(abs(m),n,cos(theta(thetaValido))).*sin(theta(thetaValido));
       % Dep(thetaValido)=diffPmn(abs(m),n,cos(theta(thetaValido)));
        
        if m==0
%             las constantes salen distintas respecto al libro por la
%             normalizacion de Pmn para m=0,-1,1
            Dep(thetaValido)=sqrt(n*(n+1))*Pmn(1,n,cos(theta(thetaValido)));
        else
            Dep(thetaValido)=-0.5*(sqrt((n-abs(m)+1)*(n+abs(m)))*Pmn(abs(m)-1,n,cos(theta(thetaValido)))...
                -sqrt((n-abs(m))*(n+abs(m)+1))*Pmn(abs(m)+1,n,cos(theta(thetaValido))));
        end

        if abs(m)==1
            Dep(theta0)=-constante*n*(n+1)/2;
            Dep(thetapi)=-constante*(-1)^n*n*(n+1)/2;
            
        else
            Dep(theta0)=0;
            Dep(thetapi)=0;
        end
        
        if component==4
            Dep=-Dep;
        end
        
    case 3
        Dep=Pmn(abs(m),n,cos(theta));
%     case 4
%         Dep=-diffPmn(abs(m),n,cos(theta)).*sin(theta);
%     case 5
%         Dep=1i*m*Pmn(abs(m),n,cos(theta))./sin(theta);
end

end

