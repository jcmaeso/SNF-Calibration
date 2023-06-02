function [ R ] = Rsn_kr( s,n,kr )
%expresses the radial dependence of an outgoing spherical wave of index
%n at kr. s is used to discriminate between components
%i.e. Rsn(kr)

if s==1
    R=z3n_kr(n,kr);
elseif s==2
%     R=1/kr*(z3n_kr(n,kr)+kr*diffz3n_kr(n,kr))
    R=(n+1).*z3n_kr(n,kr)./kr-z3n_kr(n+1,kr);
    
end


end

