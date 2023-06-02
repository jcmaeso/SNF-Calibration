function [ Er,Etheta,Ephi ] = F3smn_rThetaPhi( s,m,n,kr,Theta,Phi )
%returns the r, theta and phi components of an outgoing (c=3)
%spherical wave function of indices s,m,n at the points (r,theta,phi) 
%i.e F3_smn(r,theta,phi)
if m==0
    C=1/sqrt(2*pi)*1/sqrt(n*(n+1));
else
    C=1/sqrt(2*pi)*1/sqrt(n*(n+1))*(-m/abs(m))^m;
end

if s==1
    Er=0;
    Etheta=C*Rsn_kr( 1,n,kr ).*ThetaDependence(1,m,n,Theta).*exp(1i*m*Phi);
    Ephi=C*Rsn_kr( 1,n,kr ).*ThetaDependence(2,m,n,Theta).*exp(1i*m*Phi);
elseif s==2
    Er=C*n*(n+1)./(kr).*Rsn_kr( 1,n,kr ).*ThetaDependence(3,m,n,Theta).*exp(1i*m*Phi);
    Etheta=C*Rsn_kr( 2,n,kr ).*ThetaDependence(4,m,n,Theta).*exp(1i*m*Phi);
    Ephi=C*Rsn_kr( 2,n,kr ).*ThetaDependence(5,m,n,Theta).*exp(1i*m*Phi);
end

end

