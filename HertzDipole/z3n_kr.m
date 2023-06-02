function [ z ] = z3n_kr( n,kr )
%returns the spherical Hankel function of the first kind

% z=sqrt(pi./(2*kr)).*besselh(n+0.5,1,kr);
% z=sqrt(pi./(2*kr)).*besselj(n+0.5,kr)+1i*(-1)^(n+1)*sqrt(pi./(2*kr)).*besselj(-n-0.5,kr);
z=sqrt(pi./(2*kr)).*besselj(n+0.5,kr)+1i*sqrt(pi./(2*kr)).*bessely(n+0.5,kr);

end

